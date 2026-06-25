"""FastAPI application entry point.

Demonstrates Singleton via FastAPI lifespan: the DatabasePool is created
once at startup and the same instance is shared by every request handler.
"""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr

from db_pool.application.use_cases import (
    CreateUserUseCase,
    GetPoolStatsUseCase,
    GetUserByIdUseCase,
    ListUsersUseCase,
)
from db_pool.domain.entities import CreateUserRequest
from db_pool.infrastructure.repository import PostgresUserRepository
from db_pool.infrastructure.singleton import DatabasePool


# ── Lifespan ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialise the singleton pool once; close it on shutdown.

    FastAPI lifespan replaces deprecated @app.on_event decorators.
    The pool is guaranteed to exist for every request between yield
    and the finally block.
    """
    dsn = os.environ["DATABASE_URL"]
    pool = DatabasePool()  # Singleton: same object every time
    await pool.initialise(dsn, min_size=2, max_size=10)

    repo = PostgresUserRepository(pool)  # type: ignore[arg-type]
    await repo.ensure_schema()

    try:
        yield
    finally:
        await pool.close()


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Database Connection Pool — Singleton Pattern",
    description=(
        "Demonstrates the Singleton pattern with a thread-safe async "
        "PostgreSQL connection pool shared across all FastAPI endpoints."
    ),
    version="0.1.0",
    lifespan=lifespan,
)


# ── Dependency providers (FastAPI DI) ─────────────────────────────────────────

def get_pool() -> DatabasePool:
    """Dependency that returns the Singleton pool.

    Because DatabasePool uses SingletonMeta, every call to DatabasePool()
    returns the exact same Python object — verified by identity (is) in tests.
    """
    return DatabasePool()


def get_user_repository(pool: DatabasePool = Depends(get_pool)) -> PostgresUserRepository:
    return PostgresUserRepository(pool)  # type: ignore[arg-type]


# ── Request / Response schemas ────────────────────────────────────────────────

class CreateUserBody(BaseModel):
    name: str
    email: EmailStr


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: str


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["ops"])
async def health(pool: DatabasePool = Depends(get_pool)) -> dict[str, Any]:
    """Health check that includes live pool statistics."""
    stats = await GetPoolStatsUseCase(pool).execute()  # type: ignore[arg-type]
    return {
        "status": "healthy" if pool.is_ready else "degraded",
        "singleton_id": id(pool),  # same number on every call — proves Singleton
        "pool_stats": stats.to_dict(),
    }


@app.get("/db/pool/stats", tags=["ops"])
async def pool_stats(pool: DatabasePool = Depends(get_pool)) -> dict[str, Any]:
    """Return detailed pool statistics."""
    stats = await GetPoolStatsUseCase(pool).execute()  # type: ignore[arg-type]
    return {
        "singleton_id": id(pool),
        "stats": stats.to_dict(),
    }


@app.get("/users", response_model=list[UserResponse], tags=["users"])
async def list_users(
    repo: PostgresUserRepository = Depends(get_user_repository),
) -> list[dict[str, Any]]:
    """Return all users from the database."""
    return await ListUsersUseCase(repo).execute()  # type: ignore[arg-type]


@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["users"])
async def create_user(
    body: CreateUserBody,
    repo: PostgresUserRepository = Depends(get_user_repository),
) -> dict[str, Any]:
    """Create a new user."""
    request = CreateUserRequest(name=body.name, email=body.email)
    try:
        return await CreateUserUseCase(repo).execute(request)  # type: ignore[arg-type]
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@app.get("/users/{user_id}", response_model=UserResponse, tags=["users"])
async def get_user(
    user_id: int,
    repo: PostgresUserRepository = Depends(get_user_repository),
) -> dict[str, Any]:
    """Return a single user by ID."""
    user = await GetUserByIdUseCase(repo).execute(user_id)  # type: ignore[arg-type]
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found")
    return user
