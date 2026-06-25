"""FastAPI application — Session Token Cache using Flyweight pattern."""

from __future__ import annotations

import os
from functools import lru_cache

import redis
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel

from session_cache.application.use_cases import (
    BulkLoginUseCase,
    GetCacheStatsUseCase,
    GetSessionUseCase,
    LoginUseCase,
    SessionNotFoundError,
)
from session_cache.domain.entities import CacheStats, UserSession
from session_cache.infrastructure.factory import RedisSessionMetadataFactory
from session_cache.infrastructure.repository import RedisSessionRepository

app = FastAPI(
    title="Session Token Cache — Flyweight Pattern",
    description=(
        "Demonstrates the Flyweight pattern: 1000 sessions share N SessionMetadata "
        "objects (N = number of roles), eliminating redundant permission data."
    ),
    version="0.1.0",
)

# ── Dependency providers ──────────────────────────────────────────────────────


@lru_cache
def get_redis() -> redis.Redis:
    """Single Redis client per process — cached so `get_factory` reuses it."""
    return redis.Redis(
        host=os.environ.get("REDIS_HOST", "localhost"),
        port=int(os.environ.get("REDIS_PORT", "6379")),
        password=os.environ.get("REDIS_PASSWORD", "secret"),
        decode_responses=False,
    )


@lru_cache
def get_factory(
    r: redis.Redis = Depends(get_redis),
) -> RedisSessionMetadataFactory:
    """Single factory per process — its in-memory cache must persist across requests
    for the Flyweight pattern's memory savings to actually materialize."""
    return RedisSessionMetadataFactory(
        redis_client=r,
        app_version=os.environ.get("APP_VERSION", "1.0.0"),
    )


@lru_cache
def get_repository(
    r: redis.Redis = Depends(get_redis),
    factory: RedisSessionMetadataFactory = Depends(get_factory),
) -> RedisSessionRepository:
    return RedisSessionRepository(redis_client=r, factory=factory)


# ── Request/Response schemas ──────────────────────────────────────────────────


class LoginRequest(BaseModel):
    user_id: str
    role: str


class LoginResponse(BaseModel):
    token: str
    user_id: str
    role: str
    expires_at: str
    flyweight_id: int  # id() of the SessionMetadata object — proves sharing


class SessionResponse(BaseModel):
    user_id: str
    token: str
    role: str
    permissions: list[str]
    expires_at: str
    flyweight_id: int


class StatsResponse(BaseModel):
    total_sessions: int
    unique_flyweights: int
    estimated_bytes_without_flyweight: int
    estimated_bytes_with_flyweight: int
    memory_saved_bytes: int
    savings_percentage: float
    explanation: str


class BulkLoginRequest(BaseModel):
    count: int = 1000
    roles: list[str] = ["admin", "editor", "viewer", "moderator", "analyst"]


# ── Routes ────────────────────────────────────────────────────────────────────


@app.post(
    "/auth/login", response_model=LoginResponse, status_code=status.HTTP_201_CREATED
)
def login(
    request: LoginRequest,
    factory: RedisSessionMetadataFactory = Depends(get_factory),
    repository: RedisSessionRepository = Depends(get_repository),
) -> LoginResponse:
    """Create a new session. The role's Flyweight is reused from cache."""
    use_case = LoginUseCase(factory=factory, repository=repository)
    session: UserSession = use_case.execute(user_id=request.user_id, role=request.role)
    factory.increment_session_counter()
    return LoginResponse(
        token=session.token,
        user_id=session.user_id,
        role=session.role,
        expires_at=session.expires_at.isoformat(),
        flyweight_id=id(session.metadata),  # Python object id — shows sharing
    )


@app.get("/auth/session/{token}", response_model=SessionResponse)
def get_session(
    token: str,
    factory: RedisSessionMetadataFactory = Depends(get_factory),
    repository: RedisSessionRepository = Depends(get_repository),
) -> SessionResponse:
    """Retrieve session. Flyweight is reconstructed from role key, not raw data."""
    use_case = GetSessionUseCase(factory=factory, repository=repository)
    try:
        session: UserSession = use_case.execute(token=token)
    except SessionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc

    return SessionResponse(
        user_id=session.user_id,
        token=session.token,
        role=session.role,
        permissions=sorted(session.permissions),
        expires_at=session.expires_at.isoformat(),
        flyweight_id=id(session.metadata),
    )


@app.get("/cache/stats", response_model=StatsResponse)
def cache_stats(
    factory: RedisSessionMetadataFactory = Depends(get_factory),
) -> StatsResponse:
    """Show Flyweight memory economy statistics."""
    use_case = GetCacheStatsUseCase(factory=factory)
    stats: CacheStats = use_case.execute()
    return StatsResponse(
        total_sessions=stats.total_sessions,
        unique_flyweights=stats.unique_flyweights,
        estimated_bytes_without_flyweight=stats.estimated_bytes_without_flyweight,
        estimated_bytes_with_flyweight=stats.estimated_bytes_with_flyweight,
        memory_saved_bytes=stats.memory_saved_bytes,
        savings_percentage=round(stats.savings_percentage, 2),
        explanation=(
            f"{stats.total_sessions} sessions share only {stats.unique_flyweights} "
            f"SessionMetadata objects. Without Flyweight each session would duplicate "
            f"~2 KB of permission data."
        ),
    )


@app.post("/demo/bulk-login")
def bulk_login(
    request: BulkLoginRequest,
    factory: RedisSessionMetadataFactory = Depends(get_factory),
    repository: RedisSessionRepository = Depends(get_repository),
) -> dict[str, object]:
    """Create many sessions to demonstrate Flyweight economy."""
    login_uc = LoginUseCase(factory=factory, repository=repository)
    bulk_uc = BulkLoginUseCase(login_use_case=login_uc)
    distribution = bulk_uc.execute(count=request.count, roles=request.roles)

    for _ in range(request.count):
        factory.increment_session_counter()

    stats = factory.get_cache_stats()
    return {
        "sessions_created": request.count,
        "distribution": distribution,
        "flyweights_used": factory.get_flyweight_count(),
        "memory_stats": stats,
        "key_insight": (
            f"{request.count} sessions → {factory.get_flyweight_count()} flyweights. "
            f"Ratio: {request.count / max(factory.get_flyweight_count(), 1):.0f}:1"
        ),
    }
