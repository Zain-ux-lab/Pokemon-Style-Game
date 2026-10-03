"""Tests for the tactical bot's engine adapter and action selection."""

import copy

import pytest

from backend.bot.adapter import Action, legal_actions, simulate
from backend.bot.search import choose_action
from backend.engine.creature import Creature
from backend.engine.moves import Move
from backend.engine.turn_engine import BattleState


def creature(name, *, hp=30, attack=10, defense=10, moves=()):
    return Creature(name, hp, attack, defense, tuple(moves))


def test_legal_actions_include_moves_and_living_reserves():
    strike = Move("Strike", 10)
    state = BattleState([creature("A", moves=[strike]), creature("Reserve")], [creature("B")])

    assert legal_actions(state) == (Action("move", 0), Action("switch", 1))


def test_knockout_replacement_only_offers_living_reserves():
    state = BattleState([creature("Fainted"), creature("Reserve")], [creature("B")])
    state.team_one[0].current_hp = 0
    state.replacement_required = 0

    assert legal_actions(state) == (Action("replace", 1),)


def test_simulate_uses_engine_without_mutating_original_state():
    strike = Move("Strike", 10)
    state = BattleState([creature("A", moves=[strike])], [creature("B")])
    original = copy.deepcopy(state)

    result = simulate(state, Action("move", 0))

    assert state == original
    assert result.team_two[0].current_hp == 20
    assert result.current_player == 1


def test_simulate_rejects_an_illegal_action():
    state = BattleState([creature("A")], [creature("B")])

    with pytest.raises(ValueError, match="not legal"):
        simulate(state, Action("switch", 0))


def test_bot_takes_a_winning_move():
    weak = Move("Weak", 1)
    finisher = Move("Finish", 10)
    state = BattleState(
        [creature("Bot", hp=30, attack=10, moves=[weak, finisher])],
        [creature("Human", hp=10, defense=10, moves=[weak])],
    )

    assert choose_action(state, bot_player=0) == Action("move", 1)


def test_bot_can_choose_for_either_player_index():
    weak = Move("Weak", 1)
    finisher = Move("Finish", 10)
    state = BattleState(
        [creature("Human", hp=10, defense=10, moves=[weak])],
        [creature("Bot", hp=30, attack=10, moves=[weak, finisher])],
        current_player=1,
    )

    assert choose_action(state, bot_player=1) == Action("move", 1)


def test_equal_scores_keep_stable_action_order():
    move = Move("Strike", 1)
    state = BattleState(
        [creature("Bot", attack=0, moves=[move, move])],
        [creature("Human")],
    )

    assert choose_action(state, bot_player=0) == Action("move", 0)


def test_search_does_not_mutate_the_live_battle():
    strike = Move("Strike", 10)
    state = BattleState(
        [creature("Bot", moves=[strike]), creature("Reserve")],
        [creature("Human", moves=[strike])],
    )
    original = copy.deepcopy(state)

    choose_action(state, bot_player=0)

    assert state == original


def test_bot_switches_to_avoid_losing_its_active_creature():
    strike = Move("Strike", 10)
    state = BattleState(
        [
            creature("Exposed", hp=10, defense=10, moves=[strike]),
            creature("Durable", hp=40, defense=10, moves=[strike]),
        ],
        [creature("Opponent", hp=30, attack=10, moves=[strike])],
    )

    assert choose_action(state, bot_player=0) == Action("switch", 1)


def test_bot_selects_forced_replacement_without_spending_turn():
    state = BattleState([creature("Fainted"), creature("Reserve")], [creature("Opponent")])
    state.team_one[0].current_hp = 0
    state.replacement_required = 0

    assert choose_action(state, bot_player=0) == Action("replace", 1)


def test_bot_returns_none_when_waiting_or_battle_is_over():
    strike = Move("Strike", 10)
    state = BattleState([creature("A", moves=[strike])], [creature("B", moves=[strike])])
    finished = copy.deepcopy(state)
    finished.winner = 0

    assert choose_action(state, bot_player=1) is None
    assert choose_action(finished, bot_player=0) is None


def test_bot_heals_to_survive_the_next_attack():
    weak = Move('Scratch', 1)
    heal = Move('Recover', effect='heal', effect_amount=25)
    attacker = Move('Strike', 10)
    bot = creature('Bot', hp=30, moves=[weak, heal])
    bot.current_hp = 5
    state = BattleState([bot], [creature('Human', moves=[attacker])])

    assert choose_action(state, bot_player=0) == Action('move', 1)


def test_bot_guards_to_survive_the_next_attack():
    weak = Move('Scratch', 1)
    guard = Move('Guard', effect='guard', effect_amount=50)
    attacker = Move('Strike', 10)
    bot = creature('Bot', hp=10, moves=[weak, guard])
    bot.current_hp = 6
    state = BattleState([bot], [creature('Human', moves=[attacker])])

    assert choose_action(state, bot_player=0) == Action('move', 1)
