import pytest

from backend.api.routes import _move_view
from backend.engine.creature import Creature
from backend.engine.moves import Move
from backend.engine.turn_engine import BattleState, resolve_turn
from backend.roster import ROSTER


def creature(name, move, **kwargs):
    return Creature(name, 100, 10, 10, (move,), **kwargs)


def test_base_preview_stays_constant_across_types_guard_and_low_hp():
    move = Move('Bolt', 20, damage_type='Magic')
    actor = creature('Actor', move)
    for kind, expected in [('Physical',25),('Spirit',16),('Magic',20)]:
        target = creature('Target', Move('Hit',20), battle_type=kind)
        preview = _move_view(actor,target,move)
        assert preview['baseDamage'] == 20
        assert preview['amount'] == expected
        target.current_hp=2
        target.guard_percent=30
        assert _move_view(actor,target,move)['baseDamage']==20
        assert _move_view(actor,target,move)['amount']==2


@pytest.mark.parametrize('damage, hp, healing', [(16,50,4),(40,50,4),(8,50,2),(3,50,0),(20,99,1)])
def test_siphon_quarter_healing_capped_and_based_on_actual_hp_loss(damage,hp,healing):
    move=Move('Drain',40,mechanic='drain')
    actor=creature('Actor',move,current_hp=hp)
    target=creature('Target',Move('Hit',20),current_hp=damage)
    preview=_move_view(actor,target,move)
    result=resolve_turn(BattleState([actor],[target]),move)
    assert result.damage==damage
    assert result.healed==healing==preview['healing']
    assert actor.current_hp==hp+healing


def test_every_roster_guard_hits_and_protects_next_attack():
    guards=[(c,m) for c in ROSTER for m in c['moves'] if m.get('effect')=='guard']
    assert len(guards)==4
    for c, definition in guards:
        move=Move(**definition)
        assert move.power==12 and move.effect_amount==30
        actor=creature(c['name'],move,battle_type=c['type'])
        hit=Move('Hit',20)
        target=creature('Target',hit)
        preview=_move_view(actor,target,move)
        s=BattleState([actor],[target])
        result=resolve_turn(s,move)
        assert result.damage==12==preview['amount']
        assert result.guard_percent==30==preview['guardPercent']
        assert actor.guard_percent==30
        assert preview['effect']=='damage'
        assert resolve_turn(s,hit).damage==14
        assert actor.guard_percent==0
