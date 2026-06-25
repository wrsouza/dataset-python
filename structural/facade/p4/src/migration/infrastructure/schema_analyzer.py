"""Dialect-agnostic schema introspection via the DB-API cursor.description."""

from __future__ import annotations

from typing import Any

from migration.domain.entities import ColumnInfo, TableSchema
from migration.domain.interfaces import SchemaAnalyzer
from migration.infrastructure.identifiers import validate_table_name


class GenericSchemaAnalyzer(SchemaAnalyzer):
    """Works for sqlite3, pymysql, and psycopg2 alike: all expose `description`."""

    def analyze(self, connection: Any, table: str) -> TableSchema:
        validate_table_name(table)
        cursor = connection.cursor()
        try:
            cursor.execute(f"SELECT * FROM {table} LIMIT 0")
            columns = [
                ColumnInfo(name=col[0], data_type=str(col[1]))
                for col in cursor.description
            ]
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            row_count = cursor.fetchone()[0]
        finally:
            cursor.close()
        return TableSchema(table_name=table, columns=columns, row_count=row_count)
