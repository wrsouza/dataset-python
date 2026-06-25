"""PostgreSQL repository for import records."""

from __future__ import annotations

import os

import psycopg2
import psycopg2.extras
from psycopg2.extensions import cursor as psycopg2_cursor


class PostgresImportRepository:
    """Handles bulk insertion of import records into PostgreSQL."""

    def __init__(self) -> None:
        self._dsn = os.environ["DATABASE_URL"]

    def bulk_insert(self, records: list[dict[str, object]]) -> int:
        if not records:
            return 0

        conn = psycopg2.connect(self._dsn)
        try:
            with conn, conn.cursor() as cur:
                self._ensure_table(cur)
                psycopg2.extras.execute_values(
                    cur,
                    """
                    INSERT INTO import_records
                        (external_id, name, value, source_format, metadata)
                    VALUES %s
                    ON CONFLICT (external_id) DO UPDATE
                        SET name = EXCLUDED.name,
                            value = EXCLUDED.value,
                            source_format = EXCLUDED.source_format
                    """,
                    [
                        (
                            r.get("external_id"),
                            r.get("name"),
                            r.get("value"),
                            r.get("source_format"),
                            psycopg2.extras.Json(r.get("metadata", {})),
                        )
                        for r in records
                    ],
                )
                return int(cur.rowcount)
        finally:
            conn.close()

    @staticmethod
    def _ensure_table(cur: psycopg2_cursor) -> None:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS import_records (
                id            SERIAL PRIMARY KEY,
                external_id   TEXT UNIQUE NOT NULL,
                name          TEXT NOT NULL,
                value         NUMERIC,
                source_format TEXT,
                metadata      JSONB DEFAULT '{}',
                imported_at   TIMESTAMPTZ DEFAULT now()
            )
            """)
