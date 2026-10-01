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
    with pytest.raises(ValueError):
        Move("Heal", effect="heal", effect_amount=0)
    with pytest.raises(ValueError):
        Move("Guard", effect="guard", effect_amount=101)


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


def test_healing_move_restores_hp_up_to_max_and_consumes_turn():
    heal = Move("Lantern Flare", effect="heal", effect_amount=25)
    hit = Move("Hit", 10)
    healer = creature("Glowmire", hp=90, moves=[heal, hit], attack=10)
    healer.current_hp = 80
    state = BattleState([healer], [creature("Opponent")])

    result = resolve_turn(state, heal)

    assert result.damage == 0
    assert result.healed == 10
    assert healer.current_hp == 90
    assert state.active_creature(1).current_hp == 30
    assert state.current_player == 1


def test_healing_at_max_hp_still_uses_turn_without_overhealing():
    heal = Move("Soft Wing", effect="heal", effect_amount=20)
    state = BattleState([creature("Hushwing", moves=[heal])], [creature("Opponent")])

    result = resolve_turn(state, heal)

    assert result.healed == 0
    assert state.active_creature(0).current_hp == 30
    assert state.current_player == 1


def test_guard_reduces_next_hit_by_half_then_is_consumed():
    guard = Move("Root Snare", effect="guard", effect_amount=50)
    hit = Move("Hit", 10)
    defender = creature("Bramblebelly", moves=[guard, hit])
    attacker = creature("Opponent", moves=[hit])
    state = BattleState([defender], [attacker])

    guarded = resolve_turn(state, guard)
    assert guarded.damage == 0
    assert guarded.guard_percent == 50
    assert defender.guard_percent == 50
    assert state.current_player == 1

    first_hit = resolve_turn(state, hit)
    assert first_hit.damage == 5
    assert defender.current_hp == 25
    assert defender.guard_percent == 0
    assert state.current_player == 0

    resolve_turn(state, hit)
    second_hit = resolve_turn(state, hit)
    assert second_hit.damage == 10
    assert defender.current_hp == 5


def test_guard_can_prevent_knockout_and_does_not_persist_after_hit():
    guard = Move("Shield Bash", effect="guard", effect_amount=50)
    hit = Move("Hit", 10)
    protected = creature("Bastion", hp=30, moves=[guard])
    protected.current_hp = 6
    attacker = creature("Opponent", attack=10, moves=[hit])
    state = BattleState([protected], [attacker])

    resolve_turn(state, guard)
    result = resolve_turn(state, hit)

    assert result.damage == 5
    assert not result.knocked_out
    assert protected.current_hp == 1
    assert protected.guard_percent == 0
    assert state.winner is None


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


def test_voluntary_switch_consumes_turn_and_rejects_invalid_targets():
    hit = Move("Hit", 10)
    state = BattleState(
        [creature("A", moves=[hit]), creature("Reserve")],
        [creature("B")],
    )

    switch_active(state, 1)

    assert state.active_creature(0).name == "Reserve"
    assert state.current_player == 1
    with pytest.raises(ValueError, match="already active"):
        switch_active(state, 0)

    state_with_fainted_reserve = BattleState(
        [creature("A"), Creature("Fainted", 30, 10, 10, current_hp=0)],
        [creature("B")],
    )
    with pytest.raises(ValueError, match="knocked-out"):
        switch_active(state_with_fainted_reserve, 1)
