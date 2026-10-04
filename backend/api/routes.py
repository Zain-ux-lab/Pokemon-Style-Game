"""Single-player browser sessions using the shared engine and tactical bot."""
from copy import deepcopy
from dataclasses import dataclass, field
from random import sample
from secrets import token_urlsafe
from threading import RLock
from time import monotonic
from typing import Literal

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field, StrictInt

from backend.bot.adapter import Action, legal_actions, simulate
from backend.bot.search import choose_action
from backend.engine.creature import Creature
from backend.engine.damage import direct_damage, recoil_damage
from backend.engine.status_effects import DESCRIPTIONS
from backend.engine.type_chart import effectiveness_percent
from backend.roster import ROSTER, BY_ID
from backend.engine.moves import Move
from backend.engine.turn_engine import BattleState

router = APIRouter(prefix='/api')
COOKIE = 'battlelab_session'
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


# Local demo storage: one process. Use a shared store before running workers.
# ponytail: serialize local requests; use per-match locks if concurrent load matters.
_matches: dict[str, Match] = {}
_lock = RLock()


class TeamRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    roster: list[str] = Field(min_length=3, max_length=3)


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
        return dict(name=move.name, effect='heal', amount=min(move.effect_amount, creature.max_hp - creature.current_hp),
                    description=f'Restores up to {move.effect_amount} HP. Uses your turn.' + echo_note, symbol='＋', **metadata)
    if move.effect == 'guard':
        return dict(name=move.name, effect='guard', amount=move.effect_amount,
                    description=f'Reduces the next incoming hit by {move.effect_amount}%. Uses your turn.' + echo_note, symbol='◈', **metadata)
    if move.effect == 'status' and move.power == 0:
        return dict(name=move.name, effect='status', amount=0, description=DESCRIPTIONS[move.mechanic] + echo_note,
                    symbol='◎', **metadata)
    damage = direct_damage(creature, target, move)
    healed = min(damage // 2, creature.max_hp - creature.current_hp) if move.mechanic == 'drain' else 0
    recoil = min(creature.current_hp + healed, recoil_damage(creature, target, move))
    delayed = min(10, target.current_hp - damage) if 'echo' in creature.statuses and creature.current_hp + healed > recoil else 0
    metadata['delayedDamage'] = delayed
    description = f'{move.damage_type} / {"contact" if move.contact else "ranged"}. '
    description += DESCRIPTIONS.get(move.mechanic, 'A direct attack.')
    if recoil:
        description += f' Causes {recoil} self-damage.'
    if delayed:
        description += f' Pending echo deals {delayed} additional damage this action.'
    return dict(name=move.name, effect='damage', amount=damage, healing=healed, selfDamage=recoil,
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
                'statuses': [dict(name=name, turnsRemaining=status.turns, moveIndex=status.slot,
                                  description=DESCRIPTIONS[name]) for name, status in creature.statuses.items()],
                'switchBlockedReason': 'Paralysed until after the next action.' if 'paralyse' in creature.statuses else None,
                'moves': [_move_view(creature, target, move) for move in creature.moves],
            })
        teams.append(team)
    human_actions = legal_actions(state) if (state.replacement_required if state.replacement_required is not None else state.current_player) == 0 else ()
    return dict(teams=teams, active=state.active_indices[:], player=state.current_player,
                replacement=state.replacement_required, winner=state.winner,
                turn=match.turn, revision=match.revision, log=match.log[:],
                actions=[dict(kind=a.kind, index=a.index) for a in human_actions])


def _advance(match: Match, action: Action) -> dict:
    state = match.battle
    player = state.replacement_required if state.replacement_required is not None else state.current_player
    label = 'You' if player == 0 else 'Bot'
    actor = state.active_creature(player)
    if action.kind == 'move':
        target = state.active_creature(1 - player)
        actor_hp = actor.current_hp
        move = actor.moves[action.index]
        match.battle = simulate(state, action)
        target_after = match.battle.active_creature(1 - player)
        if move.effect == 'heal':
            restored = match.battle.active_creature(player).current_hp - actor_hp
            message = f'{label} · {actor.name} used {move.name} — restored {restored} HP.'
        elif move.effect == 'guard':
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
        if move.power > 0:
            frame['animation']['target'] = 1 - player
    return frame


@router.get('/roster')
def roster():
    # Preserve selection cards while exposing offensive status metadata.
    result = deepcopy(ROSTER)
    for character in result:
        for move in character['moves']:
            if move.get('effect') == 'status' and move.get('power', 0) > 0:
                del move['effect']
                move['appliesStatus'] = move['mechanic']
                move['description'] = DESCRIPTIONS[move['mechanic']]
    return result


@router.post('/battle')
def new_battle(data: TeamRequest, request: Request, response: Response):
    if len(set(data.roster)) != 3 or any(c not in BY_ID for c in data.roster):
        raise HTTPException(422, 'Choose three different characters from the roster.')
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
        teams = [[Creature(BY_ID[c]['name'], BY_ID[c]['maxHp'], 10, 10,
                           tuple(Move(**move) for move in BY_ID[c]['moves']), battle_type=BY_ID[c]['type']) for c in ids] for ids in rosters]
        match = Match(BattleState(*teams), rosters)
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
