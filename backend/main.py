"""Run the local single-player game: python -m uvicorn backend.main:app."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.api.routes import router

app = FastAPI(title='Clashbound')
app.include_router(router)


@app.middleware('http')
async def no_cached_battles(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-store'
    return response


@app.get('/health')
def health():
    return {'status': 'ok'}


app.mount('/', StaticFiles(directory=Path(__file__).resolve().parent.parent / 'frontend', html=True), name='frontend')
