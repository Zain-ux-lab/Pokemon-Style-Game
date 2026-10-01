"""Alternating-turn battle state and action resolution."""

from dataclasses import dataclass, field

from .creature import Creature
from .damage import calculate_damage
from .moves import Move


@dataclass
class BattleState:
    """Two locked teams with one active creature and one current player each."""

    team_one: list[Creature]
    team_two: list[Creature]
    current_player: int = 0
    active_indices: list[int] = field(default_factory=lambda: [0, 0])
    replacement_required: int | None = None
    winner: int | None = None

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

    damage = healed = guard_percent = 0
    knocked_out = False
    if move.effect == "damage":
        damage = calculate_damage(attacker, defender, move)
        if defender.guard_percent:
            damage = damage * (100 - defender.guard_percent) // 100
            defender.guard_percent = 0
        defender.current_hp = max(0, defender.current_hp - damage)
        knocked_out = defender.is_knocked_out
    elif move.effect == "heal":
        healed = min(move.effect_amount, attacker.max_hp - attacker.current_hp)
        attacker.current_hp += healed
    else:
        guard_percent = move.effect_amount
        attacker.guard_percent = guard_percent

    state.current_player = 1 - player
    if knocked_out:
        if any(not creature.is_knocked_out for creature in state.team(1 - player)):
            state.replacement_required = 1 - player
        else:
            state.winner = player

    return TurnResult(player, damage, knocked_out, state.winner, healed, guard_percent)


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
    state.active_indices[player] = new_active_index
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
    state.active_indices[player] = new_active_index
    state.replacement_required = None
