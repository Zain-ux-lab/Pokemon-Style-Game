from fastapi.testclient import TestClient
from backend.main import app


def test_arena_persists_through_actions_and_refresh_and_does_not_repeat():
    with TestClient(app) as client:
        previous=None
        for _ in range(10):
            state=client.post('/api/battle',json={'roster':['mage','sporestag','glowmire']}).json()['state']
            arena=state['arena']
            assert arena['id']!=previous
            previous=arena['id']
            image=client.get('/'+arena['image'])
            assert image.status_code==200 and image.headers['content-type']=='image/png'
            assert client.get('/api/battle').json()['state']['arena']==arena
            result=client.post('/api/battle/actions',json={'kind':'move','index':0,'revision':state['revision']}).json()
            assert all(frame['arena']==arena for frame in result['frames'])
            assert client.get('/api/battle').json()['state']['arena']==arena
