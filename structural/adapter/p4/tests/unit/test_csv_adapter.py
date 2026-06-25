"""Unit tests for CsvAdapter."""

from __future__ import annotations

import pytest

from dataframe_adapter.domain.entities import InvalidDataError
from dataframe_adapter.infrastructure.adapters import CsvAdapter


def test_csv_adapter_parses_valid_csv() -> None:
    raw_bytes = b"name,age\nAna,30\nBob,25\n"
    dataset = CsvAdapter().load(raw_bytes)
    assert dataset.columns == ["name", "age"]
    assert dataset.rows == [["Ana", "30"], ["Bob", "25"]]
    assert dataset.source_format == "csv"
    assert dataset.row_count == 2


def test_csv_adapter_raises_on_empty_file() -> None:
    with pytest.raises(InvalidDataError) as exc_info:
        CsvAdapter().load(b"")
    assert exc_info.value.source_format == "csv"


def test_csv_adapter_raises_on_invalid_encoding() -> None:
    with pytest.raises(InvalidDataError):
        CsvAdapter().load(b"\xff\xfe\x00\x01invalid")
