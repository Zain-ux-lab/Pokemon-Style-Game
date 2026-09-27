"""Unit tests for deterministic battle models and turn resolution."""

import pytest

from backend.engine.creature import Creature
from backend.engine.damage import calculate_damage
from backend.engine.moves import Move
from backend.engine.turn_engine import (
    BattleState,
    replace_knocked_out,
    resolve_turn,
    switch_active,
)


def creature(name, *, hp=30, attack=10, defense=10, moves=()):
    return Creature(name, hp, attack, defense, tuple(moves))


def test_models_validate_required_values():
    with pytest.raises(ValueError):
        Move("", 10)
    with pytest.raises(ValueError):
        Move("Strike", 0)
    with pytest.raises(ValueError):
        creature("Invalid", hp=0)


def test_damage_is_deterministic_and_uses_attack_power_and_defense():
    attacker = creature("A", attack=11)
    defender = creature("B", defense=5)
    move = Move("Hit", 7)

    assert calculate_damage(attacker, defender, move) == 15
    assert calculate_damage(attacker, defender, move) == 15


def test_turns_alternate_and_move_reduces_health():
    hit = Move("Hit", 10)
    state = BattleState(
        [creature("A", moves=[hit])],
        [creature("B")],
    )

    result = resolve_turn(state, hit)

    assert result.damage == 10
    assert state.active_creature(1).current_hp == 20
    assert state.current_player == 1
    with pytest.raises(ValueError, match="not available"):
        resolve_turn(state, hit)


def test_knockout_requires_free_replacement_and_preserves_turn():
    hit = Move("Hit", 50)
    state = BattleState(
        [creature("A", attack=10, moves=[hit])],
        [creature("B", hp=5), creature("C", hp=12)],
    )

    result = resolve_turn(state, hit)

    assert result.knocked_out
    assert state.replacement_required == 1
    assert state.current_player == 1
    with pytest.raises(ValueError, match="replaced first"):
        resolve_turn(state, hit)

    replace_knocked_out(state, 1)
    assert state.active_creature(1).name == "C"
    assert state.current_player == 1
    assert state.replacement_required is None


def test_last_knockout_ends_battle():
    hit = Move("Hit", 50)
    state = BattleState(
        [creature("A", attack=10, moves=[hit])],
        [creature("B", hp=5)],
    )

    result = resolve_turn(state, hit)

    assert result.winner == 0
    assert state.winner == 0
    with pytest.raises(ValueError, match="already over"):
        resolve_turn(state, hit)


def test_voluntary_switch_consumes_turn_and_rejects_knockouts():
    hit = Move("Hit", 10)
    state = BattleState(
        [creature("A", moves=[hit]), creature("Reserve")],
        [creature("B")],
    )

    switch_active(state, 1)

    assert state.active_creature(0).name == "Reserve"
    assert state.current_player == 1
    with pytest.raises(ValueError, match="already active"):
        switch_active(state, 1)
