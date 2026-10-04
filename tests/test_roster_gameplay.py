import pytest

from backend.api.routes import _move_view, _snapshot, Match
from backend.engine.creature import Creature
from backend.engine.moves import Move
from backend.engine.status_effects import Status
from backend.engine.turn_engine import BattleState, resolve_turn
from backend.roster import ROSTER


@pytest.mark.parametrize('definition', ROSTER, ids=lambda c:c['id'])
def test_every_move_preview_matches_engine_with_types_guard_and_conditions(definition):
    for move_definition in definition['moves']:
        for target_type in ('Magic','Physical','Spirit'):
            moves=tuple(Move(**m) for m in definition['moves'])
            move=moves[definition['moves'].index(move_definition)]
            actor=Creature(definition['name'],definition['maxHp'],10,10,moves,current_hp=60,battle_type=definition['type'])
            target=Creature('Target',100,10,10,(Move('Hit',20),),current_hp=80,guard_percent=50,battle_type=target_type)
            actor.statuses={'spores':Status(2),'weaken':Status(2),'echo':Status(1)}
            target.statuses={'mark':Status(2),'spores':Status(2),'expose':Status(2),'thorns':Status(1)}
            actor.last_damage=24
            preview=_move_view(actor,target,move)
            s=BattleState([actor],[target])
            result=resolve_turn(s,move)
            if move.power>0:
                assert result.damage==preview['amount']
                assert actor.current_hp==60+preview['healing']-preview['selfDamage']
                assert target.current_hp==80-preview['amount']-preview['delayedDamage']
            elif move.effect=='heal':
                assert result.healed==preview['amount']
            elif move.effect=='guard':
                assert result.guard_percent==preview['amount']
            if move.power==0:
                assert 80-target.current_hp==preview['delayedDamage']
                assert 'Pending echo' in preview['description']
            assert preview['description']


def test_effects_are_visible_and_paralysis_removes_only_voluntary_switch():
    def make(c):
        return Creature(c['name'],c['maxHp'],10,10,tuple(Move(**m) for m in c['moves']),battle_type=c['type'])
    teams=[[make(c) for c in ROSTER[:3]],[make(c) for c in ROSTER[3:6]]]
    state=BattleState(*teams)
    state.active_creature(0).statuses['paralyse']=Status(1)
    match=Match(state,[[c['id'] for c in ROSTER[:3]],[c['id'] for c in ROSTER[3:6]]])
    snapshot=_snapshot(match)
    assert len(snapshot['actions'])==4
    assert all(a['kind']=='move' for a in snapshot['actions'])
    assert snapshot['teams'][0][0]['statuses'][0]['turnsRemaining']==1
    assert snapshot['teams'][0][0]['switchBlockedReason']
