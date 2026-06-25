"""Unit tests for domain entities."""

from __future__ import annotations

from data_view.domain.entities import QueryResult, Record


def test_record_get_returns_value_for_known_field() -> None:
    record = Record(fields={"name": "Alice"})
    assert record.get("name") == "Alice"


def test_record_get_returns_none_for_missing_field() -> None:
    record = Record(fields={"name": "Alice"})
    assert record.get("missing") is None


def test_query_result_is_empty_true_for_no_records() -> None:
    result = QueryResult(source_name="Fake", records=[])
    assert result.is_empty() is True


def test_query_result_is_empty_false_when_records_present(
    sample_query_result: QueryResult,
) -> None:
    assert sample_query_result.is_empty() is False


def test_query_result_column_names_preserves_order(
    sample_query_result: QueryResult,
) -> None:
    assert sample_query_result.column_names() == ["name", "age"]


def test_query_result_to_rows_returns_field_dicts(
    sample_query_result: QueryResult,
) -> None:
    rows = sample_query_result.to_rows()
    assert rows == [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
