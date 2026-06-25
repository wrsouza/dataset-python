"""Loads transformed rows into the destination table via executemany."""

from __future__ import annotations

from typing import Any

from migration.domain.interfaces import DataLoader, Row
from migration.infrastructure.identifiers import validate_table_name

_PARAM_STYLE_BY_DIALECT = {
    "mysql": "%s",
    "postgresql": "%s",
    "sqlite": "?",
}


class GenericDataLoader(DataLoader):
    def __init__(self, dialect: str) -> None:
        self._placeholder = _PARAM_STYLE_BY_DIALECT.get(dialect, "?")

    def load(self, connection: Any, table: str, rows: list[Row]) -> int:
        validate_table_name(table)
        if not rows:
            return 0

        columns = list(rows[0].keys())
        placeholders = ", ".join([self._placeholder] * len(columns))
        column_list = ", ".join(columns)
        sql = f"INSERT INTO {table} ({column_list}) VALUES ({placeholders})"

        cursor = connection.cursor()
        try:
            cursor.executemany(
                sql, [tuple(row[col] for col in columns) for row in rows]
            )
            connection.commit()
        finally:
            cursor.close()
        return len(rows)
