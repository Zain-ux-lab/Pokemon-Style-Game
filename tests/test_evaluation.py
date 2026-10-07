import importlib.util
import random


def evaluation():
    assert importlib.util.find_spec('backend.bot.evaluation'), 'Evaluation runner is not implemented yet'
    from backend.bot import evaluation
    return evaluation


def test_seeded_fixtures_are_disjoint_and_keep_signature_moves():
    module = evaluation()
    fixtures = module.make_fixtures(42, 3)
    assert fixtures == module.make_fixtures(42, 3)
    from backend.roster import ROSTER
    roster = {entry['id']: entry for entry in ROSTER}
    for fixture in fixtures:
        assert len({character['id'] for team in fixture for character in team}) == 6
        for team in fixture:
            for character in team:
                assert len(set(character['moves'])) == 4
                assert set(roster[character['id']]['signatureMoves']) <= set(character['moves'])


def test_damage_baseline_selects_finishing_attack_without_mutating_state():
    module = evaluation()
    from backend.engine.creature import Creature
    from backend.engine.moves import Move
    from backend.engine.turn_engine import BattleState
    state = BattleState([Creature('A', 20, 10, 10, (Move('Small', 1), Move('Finish', 30)))],
                        [Creature('B', 20, 10, 10, (Move('Hit', 1),))])
    action = module.baseline_action(state, 'damage', random.Random(1))
    assert action.index == 1
    assert state.team_two[0].current_hp == 20


def test_action_limit_reports_unfinished_instead_of_a_win():
    module = evaluation()
    result = module.play_match(module.make_fixtures(42, 1)[0], 'damage', 1, 42, 1)
    assert result['winner'] is None
    assert result['actions'] == 1
    assert result['first_player'] == 1
