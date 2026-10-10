"""Single-player browser sessions using the shared engine and tactical bot."""
from copy import deepcopy
from dataclasses import dataclass, field
from random import sample, choice
from secrets import token_urlsafe
from threading import RLock
from time import monotonic
from typing import Literal

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field, StrictInt

from backend.bot.adapter import Action, legal_actions, simulate
from backend.bot.search import choose_action
from backend.engine.creature import Creature
from backend.engine.damage import direct_damage, recoil_damage, base_damage, drain_healing, recovery_healing
from backend.engine.status_effects import DESCRIPTIONS
from backend.engine.type_chart import effectiveness_percent
from backend.roster import ROSTER, BY_ID
from backend.arenas import ARENAS
from backend.engine.moves import Move
from backend.engine.turn_engine import BattleState

router = APIRouter(prefix='/api')
COOKIE = 'clashbound_session'
SESSION_SECONDS = 1800
MAX_SESSIONS = 256


@dataclass
class Match:
    battle: BattleState
    rosters: list[list[str]]
    revision: int = 0
    turn: int = 1
    log: list[str] = field(default_factory=lambda: ['Teams revealed. You move first.'])
    touched: float = field(default_factory=monotonic)
    arena_index: int = 0


# Local demo storage: one process. Use a shared store before running workers.
# ponytail: serialize local requests; use per-match locks if concurrent load matters.
_matches: dict[str, Match] = {}
_lock = RLock()


class TeamRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    roster: list[str] = Field(min_length=3, max_length=3)
    loadouts: dict[str, list[StrictInt]] = Field(default_factory=dict)


class ActionRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    kind: Literal['move', 'switch', 'replace']
    index: StrictInt = Field(ge=0)
    revision: StrictInt = Field(ge=0)


def _get_match(request: Request) -> tuple[str, Match]:
    session = request.cookies.get(COOKIE)
    match = _matches.get(session)
    if match is None or monotonic() - match.touched > SESSION_SECONDS:
        if session in _matches:
            del _matches[session]
        raise HTTPException(404, 'Choose a team to start a new battle.')
    match.touched = monotonic()
    return session, match


def _move_view(creature: Creature, target: Creature, move: Move) -> dict:
    metadata = dict(damageType=move.damage_type, contact=move.contact, mechanic=move.mechanic,
                    pendingEcho=10 if 'echo' in creature.statuses else 0,
                    delayedDamage=min(10, target.current_hp) if 'echo' in creature.statuses else 0)
    echo_note = f' Pending echo deals {metadata["delayedDamage"]} additional damage this action.' if metadata['delayedDamage'] else ''
    if move.effect == 'heal':
        return dict(name=move.name, effect='heal', amount=recovery_healing(creature,move.effect_amount),
                    description=f'Restores up to {move.effect_amount * creature.recovery // 10} HP. Scales with Recovery.' + echo_note, symbol='＋', **metadata)
    if move.effect == 'guard' and move.power == 0:
        return dict(name=move.name, effect='guard', amount=move.effect_amount,
                    description=f'Reduces the next incoming hit by {move.effect_amount}%. Uses your turn.' + echo_note, symbol='◈', **metadata)
    if move.effect == 'status' and move.power == 0:
        return dict(name=move.name, effect='status', amount=0, description=DESCRIPTIONS[move.mechanic] + echo_note,
                    symbol='◎', **metadata)
    damage = direct_damage(creature, target, move)
    healed = drain_healing(creature, damage) if move.mechanic == 'drain' else 0
    recoil = min(creature.current_hp + healed, recoil_damage(creature, target, move))
    delayed = min(10, target.current_hp - damage) if 'echo' in creature.statuses and creature.current_hp + healed > recoil else 0
    metadata['delayedDamage'] = delayed
    description = f'{move.damage_type} / {"contact" if move.contact else "ranged"}. Scales with {"Power" if move.damage_type in {"Physical","Neutral"} else "Focus"}. '
    description += DESCRIPTIONS.get(move.mechanic, 'A direct attack.')
    if move.effect == 'guard':
        description += f' Grants {move.effect_amount}% protection against the next hit.'
    if recoil:
        description += f' Causes {recoil} self-damage.'
    if delayed:
        description += f' Pending echo deals {delayed} additional damage this action.'
    return dict(name=move.name, effect='damage', amount=damage, baseDamage=base_damage(creature,target,move),
                scalesWith='Power' if move.damage_type in {'Physical','Neutral'} else 'Focus',
                guardPercent=move.effect_amount if move.effect == 'guard' else 0, healing=healed, selfDamage=recoil,
                effectiveness=effectiveness_percent(move.damage_type, target.battle_type),
                description=description, symbol='✦', **metadata)


def _snapshot(match: Match) -> dict:
    state = match.battle
    teams = []
    for player in (0, 1):
        target = state.active_creature(1 - player)
        team = []
        for identifier, creature in zip(match.rosters[player], state.team(player)):
            info = BY_ID[identifier]
            team.append({
                'id': identifier, 'name': creature.name, 'type': info['type'], 'art': info['art'],
                'maxHp': creature.max_hp, 'hp': creature.current_hp, 'guardPercent': creature.guard_percent,
                'stats':dict(hp=creature.max_hp,power=creature.attack,focus=creature.focus,
                             armour=creature.defense,ward=creature.ward,recovery=creature.recovery),
                'statuses': [dict(name=name, turnsRemaining=status.turns, moveIndex=status.slot,
                                  description=DESCRIPTIONS[name]) for name, status in creature.statuses.items()],
                'switchBlockedReason': 'Paralysed until after the next action.' if 'paralyse' in creature.statuses else None,
                'moves': [_move_view(creature, target, move) for move in creature.moves],
            })
        teams.append(team)
    human_actions = legal_actions(state) if (state.replacement_required if state.replacement_required is not None else state.current_player) == 0 else ()
    return dict(teams=teams, arena=ARENAS[match.arena_index].copy(), active=state.active_indices[:], player=state.current_player,
                replacement=state.replacement_required, winner=state.winner,
                turn=match.turn, revision=match.revision, log=match.log[:],
                actions=[dict(kind=a.kind, index=a.index) for a in human_actions])


def _advance(match: Match, action: Action) -> dict:
    state = match.battle
    player = state.replacement_required if state.replacement_required is not None else state.current_player
    label = 'You' if player == 0 else 'Bot'
    actor = state.active_creature(player)
    before_hp = [state.active_creature(p).current_hp for p in (0,1)]
    if action.kind == 'move':
        target = state.active_creature(1 - player)
        actor_hp = actor.current_hp
        move = actor.moves[action.index]
        match.battle = simulate(state, action)
        target_after = match.battle.active_creature(1 - player)
        if move.effect == 'heal':
            restored = match.battle.active_creature(player).current_hp - actor_hp
            message = f'{label} · {actor.name} recovered {restored} HP.'
        elif move.effect == 'guard' and move.power == 0:
            message = f'{label} · {actor.name} used {move.name} — next hit reduced by {move.effect_amount}%.'
        elif move.effect == 'status' and move.power == 0:
            message = f'{label} · {actor.name} used {move.name}.'
        else:
            message = f'{label} · {actor.name} used {move.name} — {direct_damage(actor, target, move)} direct damage.'
            if target_after.is_knocked_out:
                message += f' {target.name} was knocked out.'
    else:
        match.battle = simulate(state, action)
        name = match.battle.active_creature(player).name
        message = f'{label} deployed {name}' + (' — free replacement.' if action.kind == 'replace' else ' — turn used.')
    if action.kind != 'replace':
        match.turn += 1
    match.log.append(message)
    match.log.extend(match.battle.events)
    if match.battle.winner is not None:
        match.log.append('You win!' if match.battle.winner == 0 else 'The bot wins. Try another team!')
    match.log = match.log[-100:]
    frame = _snapshot(match)
    if action.kind == 'move':
        frame['animation'] = {'kind': 'attack' if move.power > 0 else move.effect, 'actor': player}
        frame['animation']['moveName'] = move.name if move.power > 0 else None
        frame['animation']['hpChanges'] = [dict(player=p,amount=match.battle.active_creature(p).current_hp-before_hp[p])
                                         for p in (0,1) if match.battle.active_creature(p).current_hp != before_hp[p]]
        if move.power > 0:
            frame['animation']['target'] = 1 - player
    return frame


@router.get('/roster')
def roster():
    # Preserve selection cards while exposing offensive status metadata.
    result = deepcopy(ROSTER)
    for character in result:
        for move in character['moves'] + character['movePool']:
            if move.get('effect') == 'status' and move.get('power', 0) > 0:
                del move['effect']
                move['appliesStatus'] = move['mechanic']
                move['description'] = DESCRIPTIONS[move['mechanic']]
    return result


@router.post('/battle')
def new_battle(data: TeamRequest, request: Request, response: Response):
    if len(set(data.roster)) != 3 or any(c not in BY_ID for c in data.roster):
        raise HTTPException(422, 'Choose three different characters from the roster.')
    if any(c not in data.roster for c in data.loadouts):
        raise HTTPException(422, 'Move selections must belong to your chosen team.')
    for identifier, indices in data.loadouts.items():
        if (len(indices)!=4 or len(set(indices))!=4 or
            any(i<0 or i>=len(BY_ID[identifier]['movePool']) for i in indices) or
            not set(BY_ID[identifier]['signatureMoves']).issubset(indices)):
            raise HTTPException(422, 'Keep both signature moves and choose two different alternatives.')
    with _lock:
        expired = [key for key, match in _matches.items() if monotonic() - match.touched > SESSION_SECONDS]
        for key in expired:
            del _matches[key]
        session = request.cookies.get(COOKIE)
        if session not in _matches:
            if len(_matches) >= MAX_SESSIONS:
                raise HTTPException(503, 'The demo is busy. Please try again shortly.')
            session = token_urlsafe(32)
            response.set_cookie(COOKIE, session, httponly=True, samesite='strict', secure=request.url.scheme == 'https')
        rosters = [data.roster, sample([c for c in BY_ID if c not in data.roster], 3)]
        teams=[]
        for player,ids in enumerate(rosters):
            team=[]
            for c in ids:
                info=BY_ID[c]; stats=info['stats']
                if player==0:
                    indices=data.loadouts.get(c,[0,1,2,3])
                else:
                    fixed=info['signatureMoves']
                    indices=sorted(fixed+sample([i for i in range(6) if i not in fixed],2))
                moves=tuple(Move(**info['movePool'][i]) for i in indices)
                team.append(Creature(info['name'],info['maxHp'],stats['power'],stats['armour'],moves,
                                     battle_type=info['type'],focus=stats['focus'],ward=stats['ward'],recovery=stats['recovery']))
            teams.append(team)
        match = Match(BattleState(*teams), rosters)
        previous = _matches[session].arena_index if session in _matches else None
        match.arena_index = choice([i for i in range(len(ARENAS)) if i != previous])
        # A reset invalidates any outstanding request from the previous match.
        if session in _matches:
            match.revision = _matches[session].revision + 1
        _matches[session] = match
        return {'state': _snapshot(match)}


@router.get('/battle')
def battle(request: Request):
    with _lock:
        _, match = _get_match(request)
        return {'state': _snapshot(match)}


@router.post('/battle/actions')
def act(data: ActionRequest, request: Request):
    with _lock:
        session, saved = _get_match(request)
        state = saved.battle
        if saved.revision != data.revision:
            raise HTTPException(409, 'Battle changed. Reloading the latest turn.')
        if state.winner is not None:
            raise HTTPException(409, 'This battle is over. Start a new battle.')
        player = state.replacement_required if state.replacement_required is not None else state.current_player
        if player != 0:
            raise HTTPException(409, 'Wait for the bot to finish its turn.')
        action = Action(data.kind, data.index)
        if action not in legal_actions(state):
            raise HTTPException(422, 'That action is not available.')
        # Commit the human action and bot response together, so an unexpected bot
        # failure cannot leave a partially advanced battle behind.
        match = deepcopy(saved)
        match.revision += 1
        frames = [_advance(match, action)]
        while match.battle.winner is None:
            bot_action = choose_action(match.battle, 1)
            if bot_action is None:
                break
            frames.append(_advance(match, bot_action))
        _matches[session] = match
        return {'state': frames[-1], 'frames': frames}
