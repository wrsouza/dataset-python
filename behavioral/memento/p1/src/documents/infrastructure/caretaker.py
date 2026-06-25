"""PostgreSQL Caretaker — persists and retrieves DocumentMementos.

OCP: this is the concrete implementation. Swap with a different backend
by creating another class implementing DocumentCaretaker ABC.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

import asyncpg

from documents.domain.entities import (
    DocumentMemento,
    NoHistoryError,
    VersionNotFoundError,
)
from documents.domain.interfaces import DocumentCaretaker, MementoProtocol


class PostgresVersionHistory(DocumentCaretaker):
    """Stores document snapshots (mementos) in PostgreSQL document_version table.

    SRP: only manages snapshot persistence — does not modify document content.
    OCP: new caretaker backends (e.g. S3, Redis) extend DocumentCaretaker
         without touching this file.
    """

    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def save(self, document_id: str, memento: MementoProtocol) -> None:
        assert isinstance(memento, DocumentMemento)
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO document_version (document_id, version, content, metadata, author, created_at)
                VALUES ($1, $2, $3, $4::jsonb, $5, $6)
                ON CONFLICT (document_id, version) DO NOTHING
                """,
                document_id,
                memento.version,
                memento.content,
                json.dumps(memento.metadata),
                memento.author,
                memento.created_at,
            )

    async def get(self, document_id: str, version: int) -> DocumentMemento:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT version, content, metadata, author, created_at
                FROM document_version
                WHERE document_id = $1 AND version = $2
                """,
                document_id,
                version,
            )
        if row is None:
            raise VersionNotFoundError(document_id, version)
        return self._row_to_memento(row)

    async def undo(self, document_id: str) -> DocumentMemento:
        """Return the second-most-recent snapshot (previous version)."""
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT version, content, metadata, author, created_at
                FROM document_version
                WHERE document_id = $1
                ORDER BY version DESC
                LIMIT 2
                """,
                document_id,
            )
        if len(rows) < 2:
            raise NoHistoryError(document_id)
        # rows[0] is current, rows[1] is the previous one
        return self._row_to_memento(rows[1])

    async def list_versions(self, document_id: str) -> list[DocumentMemento]:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT version, content, metadata, author, created_at
                FROM document_version
                WHERE document_id = $1
                ORDER BY version ASC
                """,
                document_id,
            )
        return [self._row_to_memento(r) for r in rows]

    @staticmethod
    def _row_to_memento(row: asyncpg.Record) -> DocumentMemento:
        created_at = row["created_at"]
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        return DocumentMemento(
            content=row["content"],
            metadata=dict(row["metadata"]),
            version=row["version"],
            author=row["author"],
            created_at=created_at,
        )
