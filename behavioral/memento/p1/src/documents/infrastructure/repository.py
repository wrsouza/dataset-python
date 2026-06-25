"""PostgreSQL repository for Documents.

Infrastructure layer — concrete implementation details are isolated here.
"""
from __future__ import annotations

from typing import Any

import asyncpg

from documents.domain.entities import Document


class DocumentRepository:
    """Concrete PostgreSQL repository for Document persistence.

    SRP: only handles document CRUD — no business logic.
    """

    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def save(self, document: Document) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO document (id, title, content, metadata, current_version)
                VALUES ($1, $2, $3, $4::jsonb, $5)
                ON CONFLICT (id) DO UPDATE
                SET title = EXCLUDED.title,
                    content = EXCLUDED.content,
                    metadata = EXCLUDED.metadata,
                    current_version = EXCLUDED.current_version,
                    updated_at = NOW()
                """,
                document.id,
                document.title,
                document.content,
                document.metadata,
                document.current_version,
            )

    async def find_by_id(self, document_id: str) -> Document | None:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, title, content, metadata, current_version FROM document WHERE id = $1",
                document_id,
            )
        if row is None:
            return None
        return Document(
            id=row["id"],
            title=row["title"],
            content=row["content"],
            metadata=dict(row["metadata"]),
            current_version=row["current_version"],
        )

    async def next_version(self, document_id: str) -> int:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT MAX(version) AS max_v FROM document_version WHERE document_id = $1",
                document_id,
            )
        return (row["max_v"] or 0) + 1

    async def init_schema(self) -> None:
        """Create tables if they do not exist. Called at application startup."""
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS document (
                    id              TEXT PRIMARY KEY,
                    title           TEXT NOT NULL,
                    content         TEXT NOT NULL DEFAULT '',
                    metadata        JSONB NOT NULL DEFAULT '{}',
                    current_version INT NOT NULL DEFAULT 1,
                    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS document_version (
                    id          SERIAL PRIMARY KEY,
                    document_id TEXT NOT NULL REFERENCES document(id) ON DELETE CASCADE,
                    version     INT NOT NULL,
                    content     TEXT NOT NULL,
                    metadata    JSONB NOT NULL DEFAULT '{}',
                    author      TEXT NOT NULL,
                    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE (document_id, version)
                );
                """
            )
