"""Exercise browser-facing battles against the real engine and bot."""
from random import Random

import pytest
from fastapi.testclient import TestClient
from backend.api import routes
from backend.main import app

PICKS = ['mage', 'sporestag', 'glowmire']


@pytest.fixture(autouse=True)
def reproducible_rosters(monkeypatch):
    # Fix only the roster draw; all engine and bot decisions run unchanged.
    monkeypatch.setattr(routes, 'sample', Random(7).sample)


def start(client):
    response = client.post('/api/battle', json={'roster': PICKS})
    assert response.status_code == 200, response.text
    return response.json()['state']


def test_roster_selection_and_opponent_are_disjoint():
    with TestClient(app) as client:
        roster = client.get('/api/roster')
        assert roster.status_code == 200
        assert len(roster.json()) == 10
        assert all(len(character['moves']) == 3 for character in roster.json())
        assert all(len({move['name'] for move in character['moves']}) == 3 for character in roster.json())
        state = start(client)
        assert [c['id'] for c in state['teams'][0]] == PICKS
        enemies = [c['id'] for c in state['teams'][1]]
        assert len(set(enemies)) == 3
        assert not set(enemies).intersection(PICKS)
        assert state['player'] == 0
        assert client.get('/api/battle').json()['state'] == state


def test_special_moves_are_described_by_the_roster_and_battle_state():
    with TestClient(app) as client:
        roster = {character['id']: character for character in client.get('/api/roster').json()}
        assert roster['glowmire']['moves'][2]['effect'] == 'heal'
        assert roster['glowmire']['moves'][2]['effect_amount'] == 25
        assert roster['hushwing']['moves'][1]['effect_amount'] == 20
        assert roster['bramblebelly']['moves'][1]['effect'] == 'guard'
        assert roster['bastion']['moves'][0]['effect_amount'] == 50
        assert all(len(character['moves']) == 3 for character in roster.values())

        state = start(client)
        moves = state['teams'][0][2]['moves']
        assert moves[2]['effect'] == 'heal'
        assert moves[2]['amount'] == 0  # Glowmire starts at full HP.
        assert moves[2]['symbol'] == '＋'


def test_healing_restores_only_missing_hp_and_spends_one_action():
    with TestClient(app) as client:
        state = client.post('/api/battle', json={'roster': ['glowmire', 'mage', 'sporestag']}).json()['state']
        attack = client.post('/api/battle/actions', json={'kind': 'move', 'index': 0, 'revision': state['revision']})
        assert attack.status_code == 200
        state = attack.json()['state']
        missing_hp = state['teams'][0][0]['maxHp'] - state['teams'][0][0]['hp']
        assert missing_hp > 0
        assert state['teams'][0][0]['moves'][2]['amount'] == min(25, missing_hp)

        response = client.post('/api/battle/actions', json={'kind': 'move', 'index': 2, 'revision': state['revision']})
        assert response.status_code == 200
        frame = response.json()['frames'][0]
        assert frame['teams'][0][0]['hp'] - state['teams'][0][0]['hp'] == min(25, missing_hp)
        assert frame['teams'][1][0]['hp'] == state['teams'][1][0]['hp']
        assert frame['animation'] == {'kind': 'heal', 'actor': 0}
        assert 'restored' in frame['log'][-1]
        assert frame['player'] == 1
        assert frame['turn'] == state['turn'] + 1


def test_guard_protects_against_the_next_bot_attack():
    with TestClient(app) as client:
        state = client.post('/api/battle', json={'roster': ['bramblebelly', 'mage', 'sporestag']}).json()['state']
        response = client.post('/api/battle/actions', json={'kind': 'move', 'index': 1, 'revision': state['revision']})
        assert response.status_code == 200
        result = response.json()
        guarded = result['frames'][0]
        assert guarded['teams'][0][0]['guardPercent'] == 50
        assert guarded['teams'][1][0]['hp'] == state['teams'][1][0]['hp']
        assert guarded['animation'] == {'kind': 'guard', 'actor': 0}
        assert guarded['teams'][1][0]['moves'][0]['amount'] == state['teams'][1][0]['moves'][0]['amount'] // 2
        assert 'next hit reduced by 50%' in guarded['log'][-1]


def test_action_runs_bot_and_rejects_duplicate_submission():
    with TestClient(app) as client:
        state = start(client)
        action = {'kind': 'move', 'index': 2, 'revision': state['revision']}
        response = client.post('/api/battle/actions', json=action)
        assert response.status_code == 200
        result = response.json()
        assert len(result['frames']) >= 2
        assert result['frames'][0]['player'] == 1
        assert result['state']['player'] == 0
        target_before = state['teams'][1][0]['hp']
        target_after = result['frames'][0]['teams'][1][0]['hp']
        assert target_before - target_after == state['teams'][0][0]['moves'][2]['amount']
        assert result['frames'][0]['animation'] == {'kind': 'attack', 'actor': 0, 'target': 1}
        assert result['frames'][1]['animation']['kind'] == 'attack'
        assert result['frames'][1]['animation']['actor'] == 1
        assert client.post('/api/battle/actions', json=action).status_code == 409
        persisted = client.get('/api/battle').json()['state']
        assert {key: value for key, value in result['state'].items() if key != 'animation'} == persisted


def test_switch_uses_turn_and_bot_replies():
    with TestClient(app) as client:
        state = start(client)
        response = client.post('/api/battle/actions', json={'kind': 'switch', 'index': 1, 'revision': state['revision']})
        result = response.json()
        assert response.status_code == 200
        assert result['frames'][0]['active'][0] == 1
        assert result['frames'][0]['player'] == 1
        assert result['state']['player'] == 0
        assert result['state']['turn'] == 3


def test_invalid_input_cannot_change_battle_or_choose_bot_actions():
    with TestClient(app) as client:
        state = start(client)
        for roster in [PICKS[:2], ['mage'] * 3, ['unknown', 'mage', 'sporestag']]:
            assert client.post('/api/battle', json={'roster': roster}).status_code == 422
        for kind, index in [('move', 99), ('switch', 0), ('replace', 1), ('move', -1), ('move', True), ('move', '0')]:
            response = client.post('/api/battle/actions', json={'kind': kind, 'index': index, 'revision': state['revision']})
            assert response.status_code in (422, 409)
        assert client.get('/api/battle').json()['state'] == state


def test_browsers_have_independent_battles_and_static_app_is_served():
    with TestClient(app) as first, TestClient(app) as second:
        initial = start(first)
        assert second.get('/api/battle').status_code == 404
        start(second)
        first.post('/api/battle/actions', json={'kind': 'move', 'index': 0, 'revision': initial['revision']})
        assert second.get('/api/battle').json()['state']['revision'] == 0
        assert first.get('/').status_code == 200
        assert first.get('/script.js').status_code == 200
        assert first.get('/backend/main.py').status_code == 404


def test_complete_match_replacements_are_free_and_terminal_blocks_actions():
    with TestClient(app) as client:
        state = start(client)
        replacements = 0
        for _ in range(180):
            if state['winner'] is not None:
                break
            if state['replacement'] == 0:
                kind = 'replace'
                index = next(i for i, c in enumerate(state['teams'][0]) if c['hp'] > 0)
            else:
                kind, index = 'move', 0
            response = client.post('/api/battle/actions', json={'kind': kind, 'index': index, 'revision': state['revision']})
            assert response.status_code == 200, response.text
            result = response.json()
            if kind == 'replace':
                replacements += 1
                assert result['state']['turn'] == state['turn']
                assert result['state']['player'] == 0
                assert len(result['frames']) == 1
            state = result['state']
        assert state['winner'] in (0, 1)
        assert replacements > 0
        assert all(c['hp'] == 0 for c in state['teams'][1 - state['winner']])
        assert client.post('/api/battle/actions', json={'kind': 'move', 'index': 0, 'revision': state['revision']}).status_code == 409


def test_reset_invalidates_actions_from_previous_match():
    with TestClient(app) as client:
        old = start(client)
        new = start(client)
        assert new['revision'] > old['revision']
        response = client.post('/api/battle/actions', json={'kind': 'move', 'index': 0, 'revision': old['revision']})
        assert response.status_code == 409
        assert client.get('/api/battle').json()['state'] == new


def test_unknown_session_cookie_is_replaced_with_a_server_token():
    with TestClient(app) as client:
        supplied = 'untrusted-session-value'
        client.cookies.set(routes.COOKIE, supplied)
        response = client.post('/api/battle', json={'roster': PICKS})
        assert response.status_code == 200
        issued = response.cookies.get(routes.COOKIE)
        assert issued and issued != supplied
        assert issued in routes._matches
        assert supplied not in routes._matches
        assert 'HttpOnly' in response.headers['set-cookie']
        assert 'SameSite=strict' in response.headers['set-cookie']


def test_existing_session_reset_does_not_reissue_the_incoming_cookie():
    with TestClient(app) as client:
        previous = start(client)
        session = client.cookies.get(routes.COOKIE)
        response = client.post('/api/battle', json={'roster': PICKS})
        assert response.status_code == 200
        assert 'set-cookie' not in response.headers
        assert client.cookies.get(routes.COOKIE) == session
        current = client.get('/api/battle').json()['state']
        assert current == response.json()['state']
        assert current['revision'] > previous['revision']


def test_failed_bot_response_does_not_commit_half_a_turn(monkeypatch):
    def broken_bot(*args):
        raise RuntimeError('Unexpected engine failure')

    with TestClient(app, raise_server_exceptions=False) as client:
        state = start(client)
        monkeypatch.setattr(routes, 'choose_action', broken_bot)
        response = client.post('/api/battle/actions', json={'kind': 'move', 'index': 0, 'revision': state['revision']})
        assert response.status_code == 500
        assert client.get('/api/battle').json()['state'] == state
