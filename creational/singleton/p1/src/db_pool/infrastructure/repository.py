"""PostgreSQL-backed user repository.

Depends on the ConnectionPool abstraction (DIP), not directly on asyncpg
or the DatabasePool singleton. This allows unit tests to inject a fake pool.
"""

from __future__ import annotations

from typing import Any

import asyncpg  # type: ignore[import]

from db_pool.domain.entities import User
from db_pool.domain.interfaces import ConnectionPool


class PostgresUserRepository:
    """Concrete user repository backed by PostgreSQL.

    SRP: only responsible for translating User domain objects to/from SQL rows.
    It does not manage connections — that is the pool's responsibility.
    """

    def __init__(self, pool: ConnectionPool) -> None:
        self._pool = pool

    async def ensure_schema(self) -> None:
        """Create the users table if it does not already exist.

        Called once at startup so the app works without a migration tool.
        """
        async with self._pool.connection() as conn:  # type: ignore[attr-defined]
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id         SERIAL PRIMARY KEY,
                    name       TEXT        NOT NULL,
                    email      TEXT        NOT NULL UNIQUE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
                """
            )

    async def find_all(self) -> list[dict[str, Any]]:
        """Return all users ordered by creation date."""
        async with self._pool.connection() as conn:  # type: ignore[attr-defined]
            rows: list[asyncpg.Record] = await conn.fetch(
                "SELECT id, name, email, created_at FROM users ORDER BY created_at DESC"
            )
            return [dict(row) for row in rows]

    async def create(self, name: str, email: str) -> dict[str, Any]:
        """Insert a new user and return the persisted record."""
        async with self._pool.connection() as conn:  # type: ignore[attr-defined]
            row: asyncpg.Record = await conn.fetchrow(
                """
                INSERT INTO users (name, email)
                VALUES ($1, $2)
                RETURNING id, name, email, created_at
                """,
                name,
                email,
            )
            return dict(row)

    async def find_by_id(self, user_id: int) -> dict[str, Any] | None:
        """Return a single user by primary key, or None."""
        async with self._pool.connection() as conn:  # type: ignore[attr-defined]
            row: asyncpg.Record | None = await conn.fetchrow(
                "SELECT id, name, email, created_at FROM users WHERE id = $1",
                user_id,
            )
            return dict(row) if row else None
