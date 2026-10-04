from copy import deepcopy

import pytest

from backend.engine.creature import Creature
from backend.engine.moves import Move
from backend.engine.turn_engine import BattleState, resolve_turn, switch_active, replace_knocked_out
from backend.bot.adapter import legal_actions
from backend.bot.search import choose_action


def battle(move, target_move=None):
    hit = target_move or Move('Hit', 20, contact=True)
    a = Creature('A', 100, 10, 10, (move,))
    b = Creature('B', 100, 10, 10, (hit,))
    return BattleState([a, Creature('Reserve A',100,10,10,(hit,))],
                       [b, Creature('Reserve B',100,10,10,(hit,))])


def test_type_cycle_and_neutral_legacy_damage():
    for attack_type, target_type, expected in [('Magic','Physical',25),('Magic','Spirit',16),('Magic','Magic',20),('Neutral','Physical',20)]:
        move = Move('Hit',20,damage_type=attack_type)
        s = battle(move)
        s.active_creature(1).battle_type = target_type
        assert resolve_turn(s,move).damage == expected


def test_paralysis_blocks_switch_not_moves_and_expires():
    move = Move('Paralyse',effect='status',mechanic='paralyse')
    s = battle(move)
    resolve_turn(s,move)
    assert not any(a.kind=='switch' for a in legal_actions(s))
    before = deepcopy(s)
    with pytest.raises(ValueError): switch_active(s,1)
    assert s == before
    resolve_turn(s,s.active_creature(1).moves[0])
    assert 'paralyse' not in s.active_creature(1).statuses


def test_spores_recoil_refresh_and_switch_clearing():
    move = Move('Spores',effect='status',mechanic='spores')
    s = battle(move)
    resolve_turn(s,move)
    resolve_turn(s,s.active_creature(1).moves[0])
    assert s.active_creature(1).current_hp == 94
    assert s.active_creature(1).statuses['spores'].turns == 1
    resolve_turn(s,move)
    assert s.active_creature(1).statuses['spores'].turns == 2
    switch_active(s,1)
    assert not s.team_two[0].statuses


def test_echo_delayed_and_cancelled_on_switch():
    move = Move('Echo',15,mechanic='echo')
    s = battle(move)
    resolve_turn(s,move)
    assert s.active_creature(1).current_hp == 85
    resolve_turn(s,s.active_creature(1).moves[0])
    resolve_turn(s,move)
    assert s.active_creature(1).current_hp == 60
    s = battle(move)
    resolve_turn(s,move)
    switch_active(s,1)
    assert 'echo' not in s.active_creature(0).statuses


def test_drain_uses_actual_damage_not_overkill():
    move = Move('Drain',30,mechanic='drain')
    s = battle(move)
    s.active_creature(0).current_hp = 50
    s.active_creature(1).current_hp = 5
    result = resolve_turn(s,move)
    assert result.damage == 5
    assert s.active_creature(0).current_hp == 52


def test_thorns_only_contact_and_no_recursive_reflection():
    for contact, hp in [(True,86),(False,100)]:
        move = Move('Thorns',effect='status',mechanic='thorns')
        s = battle(move,Move('Hit',20,contact=contact))
        resolve_turn(s,move)
        resolve_turn(s,s.active_creature(1).moves[0])
        assert s.active_creature(1).current_hp == hp
        resolve_turn(s,move)
        assert s.active_creature(0).statuses['thorns'].turns == 1


def test_mark_bonus_consumes_mark():
    mark = Move('Mark',effect='status',mechanic='mark')
    shot = Move('Shot',20,mechanic='exploit')
    s = battle(mark)
    s.active_creature(0).moves=(mark,shot)
    resolve_turn(s,mark)
    resolve_turn(s,s.active_creature(1).moves[0])
    assert resolve_turn(s,shot).damage == 38
    assert 'mark' not in s.active_creature(1).statuses


def test_reprisal_and_dread_and_phase():
    counter = Move('Counter',10,mechanic='reprisal')
    s = battle(counter)
    s.current_player=1
    resolve_turn(s,s.active_creature(1).moves[0])
    assert resolve_turn(s,counter).damage == 20
    dread=Move('Dread',10,mechanic='dread')
    s=battle(dread)
    s.active_creature(1).current_hp=49
    resolve_turn(s,dread)
    assert resolve_turn(s,s.active_creature(1).moves[0]).damage==15
    phase=Move('Phase',20,mechanic='phase')
    s=battle(phase)
    s.active_creature(1).guard_percent=50
    assert resolve_turn(s,phase).damage==20
    assert s.active_creature(1).guard_percent==0


def test_confusion_marks_strongest_slot_and_recoil_is_deterministic():
    confuse=Move('Confuse',effect='status',mechanic='confuse')
    s=battle(confuse)
    s.active_creature(1).moves=(Move('Light',10),Move('Heavy',30))
    resolve_turn(s,confuse)
    assert s.active_creature(1).statuses['confuse'].slot==1
    resolve_turn(s,s.active_creature(1).moves[1])
    assert s.active_creature(1).current_hp==92


def test_two_knockouts_require_two_free_replacements():
    thorns=Move('Thorns',effect='status',mechanic='thorns')
    s=battle(thorns)
    resolve_turn(s,thorns)
    s.active_creature(0).current_hp=10
    s.active_creature(1).current_hp=6
    resolve_turn(s,s.active_creature(1).moves[0])
    assert s.replacement_required==0
    replace_knocked_out(s,1)
    assert s.replacement_required==1
    replace_knocked_out(s,1)
    assert s.replacement_required is None
    assert s.current_player==0


def test_bot_values_pending_echo_over_one_more_immediate_damage():
    echo=Move('Echo',15,mechanic='echo')
    ordinary=Move('Plain',16)
    bot=Creature('Bot',100,10,10,(ordinary,echo))
    target=Creature('Target',100,10,10,(Move('Hit',10),))
    s=BattleState([target],[bot],current_player=1)
    assert choose_action(s,1).index==1


def test_guard_and_echo_clear_when_caster_switches():
    echo=Move('Echo',15,mechanic='echo')
    s=battle(echo)
    resolve_turn(s,echo)
    resolve_turn(s,s.active_creature(1).moves[0])
    s.active_creature(0).guard_percent=50
    switch_active(s,1)
    assert not s.team_one[0].statuses
    assert s.team_one[0].guard_percent==0


def test_final_double_ko_awards_defender_not_suicide_attacker():
    s=battle(Move('Thorns',effect='status',mechanic='thorns'))
    s.team_one=s.team_one[:1]
    s.team_two=s.team_two[:1]
    resolve_turn(s,s.active_creature(0).moves[0])
    s.active_creature(0).current_hp=10
    s.active_creature(1).current_hp=6
    resolve_turn(s,s.active_creature(1).moves[0])
    assert s.winner==0
    assert not legal_actions(s)


def test_offensive_status_deals_typed_damage_then_applies_condition():
    move=Move('Static Lock',10,effect='status',mechanic='paralyse',damage_type='Magic')
    s=battle(move)
    s.active_creature(1).battle_type='Physical'
    assert resolve_turn(s,move).damage==12
    assert s.active_creature(1).statuses['paralyse'].turns==1
    assert not any(a.kind=='switch' for a in legal_actions(s))


def test_conditions_expire_after_two_holder_actions_and_refresh_does_not_stack():
    from backend.engine.status_effects import Status
    heal=Move('Rest',effect='heal',effect_amount=5)
    s=battle(heal,heal)
    s.active_creature(0).statuses={'spores':Status(2),'confuse':Status(2,0),'weaken':Status(2),'expose':Status(2)}
    resolve_turn(s,heal)
    assert all(x.turns==1 for x in s.active_creature(0).statuses.values())
    assert s.active_creature(0).current_hp==100
    resolve_turn(s,heal)
    resolve_turn(s,heal)
    assert not s.active_creature(0).statuses


def test_free_replacement_does_not_advance_survivor_effects():
    from backend.engine.status_effects import Status
    hit=Move('Hit',20)
    s=battle(hit)
    s.active_creature(0).statuses['spores']=Status(2)
    s.active_creature(1).current_hp=1
    resolve_turn(s,hit)
    assert s.active_creature(0).statuses['spores'].turns==1
    replace_knocked_out(s,1)
    assert s.active_creature(0).statuses['spores'].turns==1
