"""Tests for TrimmingTypeTransformer."""

from __future__ import annotations

from migration.domain.entities import ColumnInfo, TableSchema
from migration.infrastructure.transformer import TrimmingTypeTransformer


def test_strips_whitespace_from_string_values() -> None:
    schema = TableSchema(
        "orders", [ColumnInfo("name", "TEXT"), ColumnInfo("total", "REAL")], 1
    )
    transformer = TrimmingTypeTransformer()

    result = transformer.transform([{"name": "  Alice  ", "total": 10.5}], schema)

    assert result == [{"name": "Alice", "total": 10.5}]


def test_fills_missing_columns_with_none() -> None:
    schema = TableSchema(
        "orders", [ColumnInfo("name", "TEXT"), ColumnInfo("total", "REAL")], 1
    )
    transformer = TrimmingTypeTransformer()

    result = transformer.transform([{"name": "Bob"}], schema)

    assert result == [{"name": "Bob", "total": None}]
