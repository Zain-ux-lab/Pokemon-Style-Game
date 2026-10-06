from fastapi.testclient import TestClient
from backend.main import app
from backend.roster import BY_ID
from backend.engine.moves import Move
from backend.engine.creature import Creature
from backend.engine.damage import base_damage
from backend.engine.turn_engine import BattleState,resolve_turn


def test_focus_ward_and_power_armour_scale_separately():
    hit=Move('Magic hit',20,damage_type='Magic')
    a=Creature('A',100,12,10,(hit,),focus=15,ward=8,recovery=12)
    b=Creature('B',100,10,10,(hit,),focus=8,ward=12)
    assert base_damage(a,b,hit)==25
    assert base_damage(a,b,Move('Physical hit',20,damage_type='Physical'))==24


def test_custom_loadouts_are_locked_validated_and_persisted():
    with TestClient(app) as client:
        roster=client.get('/api/roster').json()
        assert all(len(c['movePool'])==6 and len(c['signatureMoves'])==2 for c in roster)
        picks=['mage','sporestag','glowmire']
        selected={c:BY_ID[c]['signatureMoves']+[4,5] for c in picks}
        response=client.post('/api/battle',json={'roster':picks,'loadouts':selected})
        assert response.status_code==200,response.text
        state=response.json()['state']
        for c in state['teams'][0]:
            assert [m['name'] for m in c['moves']]==[BY_ID[c['id']]['movePool'][i]['name'] for i in selected[c['id']]]
            assert set(c['stats'])=={'hp','power','focus','armour','ward','recovery'}
        assert client.get('/api/battle').json()['state']==state
        for invalid in ([0,0,1,2],[0,1,2,99],[True,1,2,3],[0,1,4,5]):
            r=client.post('/api/battle',json={'roster':picks,'loadouts':{'mage':invalid}})
            assert r.status_code==422
        assert client.get('/api/battle').json()['state']==state


def test_attack_feedback_has_name_and_exact_hp_delta():
    with TestClient(app) as client:
        s=client.post('/api/battle',json={'roster':['mage','sporestag','glowmire']}).json()['state']
        data=client.post('/api/battle/actions',json={'kind':'move','index':0,'revision':s['revision']}).json()
        frame=data['frames'][0]
        assert frame['animation']['moveName']=='Arcane Bolt'
        loss=s['teams'][1][0]['hp']-frame['teams'][1][0]['hp']
        assert any(x['player']==1 and x['amount']==-loss for x in frame['animation']['hpChanges'])


def test_recovery_stat_scales_heal_and_has_no_attack_announcement():
    heal=Move('Rest',effect='heal',effect_amount=10)
    c=Creature('Healer',100,10,10,(heal,),current_hp=60,recovery=12)
    enemy=Creature('Enemy',100,10,10,(Move('Hit',10),))
    assert resolve_turn(BattleState([c],[enemy]),heal).healed==12
    with TestClient(app) as client:
        state=client.post('/api/battle',json={'roster':['glowmire','mage','sporestag']}).json()['state']
        frame=client.post('/api/battle/actions',json={'kind':'move','index':2,'revision':state['revision']}).json()['frames'][0]
        assert frame['animation']['moveName'] is None
