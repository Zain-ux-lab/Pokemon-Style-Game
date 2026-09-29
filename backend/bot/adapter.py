"""Translate bot choices into actions handled by the battle engine."""

from copy import deepcopy
from dataclasses import dataclass
from typing import Literal

from backend.engine.turn_engine import (
    BattleState,
    replace_knocked_out,
    resolve_turn,
    switch_active,
)


@dataclass(frozen=True)
class Action:
    """An engine action; index selects a move or team member."""

    kind: Literal["move", "switch", "replace"]
    index: int

    def __post_init__(self) -> None:
        if self.kind not in {"move", "switch", "replace"}:
            raise ValueError("action kind must be move, switch, or replace")
        if not isinstance(self.index, int) or isinstance(self.index, bool):
            raise ValueError("action index must be an integer")
        if self.index < 0:
            raise ValueError("action index must not be negative")


def legal_actions(state: BattleState) -> tuple[Action, ...]:
    """List valid actions for the player who must act or replace a knockout."""
    if state.winner is not None:
        return ()

    player = state.replacement_required
    if player is not None:
        team = state.team(player)
        candidates = tuple(
            Action("replace", index)
            for index, creature in enumerate(team)
            if index != state.active_indices[player] and not creature.is_knocked_out
        )
    else:
        player = state.current_player
        active = state.active_creature(player)
        candidates = tuple(
            [Action("move", index) for index in range(len(active.moves))]
            + [
                Action("switch", index)
                for index, creature in enumerate(state.team(player))
                if index != state.active_indices[player] and not creature.is_knocked_out
            ]
        )

    valid = []
    for action in candidates:
        try:
            _apply_action(deepcopy(state), action)
        except ValueError:
            continue
        valid.append(action)
    return tuple(valid)


def simulate(state: BattleState, action: Action) -> BattleState:
    """Return a copied battle after applying a legal action through the engine."""
    if action not in legal_actions(state):
        raise ValueError("action is not legal in this battle state")
    return _apply_action(deepcopy(state), action)


def _apply_action(state: BattleState, action: Action) -> BattleState:
    if action.kind == "replace":
        replace_knocked_out(state, action.index)
    elif action.kind == "switch":
        switch_active(state, action.index)
    else:
        move = state.active_creature(state.current_player).moves[action.index]
        resolve_turn(state, move)
    return state
