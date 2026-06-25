"""Tracks which tables a migration touched so a failed run can be undone.

Simplification for an educational example: rollback means "delete every row
this migration inserted into the destination tables", which is correct for
the common case of migrating into freshly-provisioned destination tables.
"""

from __future__ import annotations

from typing import Any

from migration.infrastructure.identifiers import validate_table_name


class RollbackManager:
    def __init__(self) -> None:
        self._touched_tables: dict[str, list[str]] = {}

    def record(self, migration_id: str, table: str) -> None:
        self._touched_tables.setdefault(migration_id, []).append(table)

    def rollback(self, migration_id: str, connection: Any) -> bool:
        tables = self._touched_tables.get(migration_id)
        if not tables:
            return False

        cursor = connection.cursor()
        try:
            for table in tables:
                validate_table_name(table)
                cursor.execute(f"DELETE FROM {table}")
            connection.commit()
        finally:
            cursor.close()

        del self._touched_tables[migration_id]
        return True
