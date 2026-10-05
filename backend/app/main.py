"""
Application FastAPI principale.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import agents, auth, runs
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise la base au démarrage."""
    from app.db import init_db
    if settings.env != "production":
        await init_db()
    yield


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def extract_current_user(request: Request, call_next):
    """Injecte l'id utilisateur courant depuis le header Authorization."""
    auth_header = request.headers.get("Authorization", "")
    request.state.current_user_id = None
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
        from app.core.security import decode_token
        payload = decode_token(token)
        if payload:
            request.state.current_user_id = payload.get("sub")
    return await call_next(request)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "version": settings.api_version}


@app.get("/stats")
async def platform_stats(session=Depends()):
    """Statistiques globales de la marketplace."""
    from sqlalchemy import func, select
    from app.db import get_session
    from app.models import Agent, Run, User

    # Stub minimal (à enrichir)
    return {"total_agents": 0, "total_runs": 0, "total_users": 0, "total_revenue_cents": 0}


app.include_router(auth.router, dependencies=[Depends(lambda r: r)])
app.include_router(agents.router, dependencies=[Depends(lambda r: r)])
app.include_router(runs.router, dependencies=[Depends(lambda r: r)])


from fastapi import Depends  # noqa: E402