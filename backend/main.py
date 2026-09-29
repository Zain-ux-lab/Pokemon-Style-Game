"""
BattleLab backend entrypoint.

Owner: Backend teammate
Run with: uvicorn backend.main:app --reload
"""
from fastapi import FastAPI

app = FastAPI(title="BattleLab")


@app.get("/health")
def health():
    """Simple liveness check so the frontend/CI can confirm the server is up."""
    return {"status": "ok"}


# WebSocket battle endpoint, matchmaking routes, and auth routes get added here
# as api/ modules are built out (see backend/api/).
