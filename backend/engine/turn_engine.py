"""Alternating-turn battle state and action resolution."""

from dataclasses import dataclass, field

from .creature import Creature
from .damage import direct_damage, recoil_damage, drain_healing, recovery_healing
from .moves import Move
from .status_effects import Status, DURATIONS


@dataclass
class BattleState:
    """Two locked teams with one active creature and one current player each."""

    team_one: list[Creature]
    team_two: list[Creature]
    current_player: int = 0
    active_indices: list[int] = field(default_factory=lambda: [0, 0])
    replacement_required: int | None = None
    winner: int | None = None
    events: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.team_one or not self.team_two:
            raise ValueError("both teams must contain at least one creature")
        if self.current_player not in (0, 1):
            raise ValueError("current_player must be 0 or 1")
        if len(self.active_indices) != 2:
            raise ValueError("active_indices must contain one index per player")
        for player in (0, 1):
            team = self.team(player)
            index = self.active_indices[player]
            if not 0 <= index < len(team):
                raise ValueError("active creature index is outside its team")
            if team[index].is_knocked_out:
                raise ValueError("an active creature cannot be knocked out")

    def team(self, player: int) -> list[Creature]:
        """Return a player's locked team."""
        _validate_player(player)
        return self.team_one if player == 0 else self.team_two

    def active_creature(self, player: int) -> Creature:
        """Return a player's active creature."""
        return self.team(player)[self.active_indices[player]]


@dataclass(frozen=True)
class TurnResult:
    """Summary of one resolved move action."""

    player: int
    damage: int
    knocked_out: bool
    winner: int | None
    healed: int = 0
    guard_percent: int = 0


def _validate_player(player: int) -> None:
    if player not in (0, 1):
        raise ValueError("player must be 0 or 1")


def _ensure_action_allowed(state: BattleState) -> None:
    if state.winner is not None:
        raise ValueError("the battle is already over")
    if state.replacement_required is not None:
        raise ValueError("a knocked-out creature must be replaced first")


def resolve_turn(state: BattleState, move: Move) -> TurnResult:
    """Resolve the current player's move and pass the turn to the opponent."""
    _ensure_action_allowed(state)
    player = state.current_player
    attacker = state.active_creature(player)
    defender = state.active_creature(1 - player)
    if attacker.is_knocked_out:
        raise ValueError("a knocked-out creature cannot act")
    if move not in attacker.moves:
        raise ValueError("move is not available to the active creature")

    state.events = []
    old_statuses = dict(attacker.statuses)
    target_hp = defender.current_hp
    defender.last_damage = 0
    damage = healed = guard_percent = 0
    if move.power > 0:
        damage = direct_damage(attacker, defender, move)
        recoil = recoil_damage(attacker, defender, move)
        defender.guard_percent = 0
        defender.current_hp -= damage
        defender.last_damage = damage
        attacker.statuses.pop('weaken', None)
        defender.statuses.pop('expose', None)
        consumed = {'exploit': 'mark', 'harvest': 'spores'}.get(move.mechanic)
        if consumed:
            defender.statuses.pop(consumed, None)
        if move.mechanic == 'drain':
            healed = drain_healing(attacker, damage)
            attacker.current_hp += healed
            state.events.append(f'{attacker.name} drained {healed} HP.')
        if move.mechanic == 'dread' and target_hp * 2 < defender.max_hp and not defender.is_knocked_out:
            defender.statuses['weaken'] = Status(2)
            state.events.append(f'{defender.name} is weakened.')
        if recoil:
            lost = min(recoil, attacker.current_hp)
            attacker.current_hp -= lost
            state.events.append(f'{attacker.name} took {lost} recoil/reflection damage.')
        if move.mechanic == 'echo' and not attacker.is_knocked_out and not defender.is_knocked_out:
            attacker.statuses['echo'] = Status(1)
            state.events.append(f'{attacker.name} prepared a spell echo.')
    elif move.effect == "heal":
        healed = recovery_healing(attacker, move.effect_amount)
        attacker.current_hp += healed
    if move.effect == 'guard' and not attacker.is_knocked_out:
        guard_percent = move.effect_amount
        attacker.guard_percent = guard_percent
        state.events.append(f'{attacker.name} guards the next hit by {guard_percent}%.')
    if move.effect == 'status':
        holder = attacker if move.mechanic == 'thorns' else defender
        slot = None
        if move.mechanic == 'confuse':
            existing = holder.statuses.get('confuse')
            attacks = [i for i, candidate in enumerate(holder.moves) if candidate.power > 0]
            slot = existing.slot if existing else max(attacks, key=lambda i: holder.moves[i].power, default=None)
        if not holder.is_knocked_out:
            holder.statuses[move.mechanic] = Status(DURATIONS[move.mechanic], slot)
            state.events.append(f'{holder.name}: {move.mechanic} ({DURATIONS[move.mechanic]} action(s)).')

    # Only conditions present before this action age; reapplications refresh.
    for name, status in old_statuses.items():
        if name == 'echo':
            if not attacker.is_knocked_out and not defender.is_knocked_out:
                delayed = min(10, defender.current_hp)
                defender.current_hp -= delayed
                state.events.append(f'Spell echo dealt {delayed} damage to {defender.name}.')
            if attacker.statuses.get(name) is status:
                attacker.statuses.pop(name, None)
        elif attacker.statuses.get(name) is status:
            status.turns -= 1
            if status.turns == 0:
                del attacker.statuses[name]

    state.current_player = 1 - player
    _settle_knockouts(state, player)

    return TurnResult(player, damage, defender.is_knocked_out, state.winner, healed, guard_percent)


def _clear_departing(state: BattleState, player: int) -> None:
    creature = state.active_creature(player)
    creature.statuses.clear()
    creature.guard_percent = 0
    creature.last_damage = 0
    state.active_creature(1 - player).statuses.pop('echo', None)


def _settle_knockouts(state: BattleState, actor: int) -> None:
    alive = [any(not c.is_knocked_out for c in state.team(p)) for p in (0, 1)]
    state.replacement_required = None
    for p in (0, 1):
        if state.active_creature(p).is_knocked_out:
            _clear_departing(state, p)
    if not all(alive):
        # Recoil cannot win a match by sacrificing your final character.
        state.winner = (0 if alive[0] else 1) if any(alive) else 1 - actor
        return
    state.replacement_required = next((p for p in (0, 1) if state.active_creature(p).is_knocked_out), None)


def switch_active(state: BattleState, new_active_index: int) -> None:
    """Voluntarily switch on the current player's turn, consuming that turn."""
    _ensure_action_allowed(state)
    player = state.current_player
    team = state.team(player)
    if not 0 <= new_active_index < len(team):
        raise ValueError("replacement index is outside the player's team")
    if new_active_index == state.active_indices[player]:
        raise ValueError("the selected creature is already active")
    if team[new_active_index].is_knocked_out:
        raise ValueError("a knocked-out creature cannot be selected")
    if 'paralyse' in state.active_creature(player).statuses:
        raise ValueError("paralysis prevents voluntary switching")
    state.events = []
    _clear_departing(state, player)
    state.active_indices[player] = new_active_index
    state.active_creature(1 - player).last_damage = 0
    state.current_player = 1 - player


def replace_knocked_out(state: BattleState, new_active_index: int) -> None:
    """Freely deploy a reserve after a knockout without changing the turn."""
    player = state.replacement_required
    if player is None:
        raise ValueError("no forced replacement is pending")
    team = state.team(player)
    if not 0 <= new_active_index < len(team):
        raise ValueError("replacement index is outside the player's team")
    if new_active_index == state.active_indices[player]:
        raise ValueError("the selected creature is already active")
    if team[new_active_index].is_knocked_out:
        raise ValueError("a knocked-out creature cannot be selected")
    state.events = []
    _clear_departing(state, player)
    state.active_indices[player] = new_active_index
    _settle_knockouts(state, 1 - state.current_player)
