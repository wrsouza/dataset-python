"""Row-level cleanup before loading into the destination dialect."""

from __future__ import annotations

from migration.domain.entities import TableSchema
from migration.domain.interfaces import DataTransformer, Row


class TrimmingTypeTransformer(DataTransformer):
    """Strips string whitespace and fills missing columns with None.

    Real migrations often need dialect type coercion (e.g. MySQL TINYINT(1)
    booleans → PostgreSQL BOOLEAN); this keeps that single responsibility
    isolated here so it can grow without touching extraction or loading.
    """

    def transform(self, rows: list[Row], schema: TableSchema) -> list[Row]:
        column_names = [column.name for column in schema.columns]
        transformed: list[Row] = []
        for row in rows:
            cleaned: Row = {}
            for name in column_names:
                value = row.get(name)
                cleaned[name] = value.strip() if isinstance(value, str) else value
            transformed.append(cleaned)
        return transformed
