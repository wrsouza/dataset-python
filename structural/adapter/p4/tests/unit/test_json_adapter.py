"""Unit tests for JsonAdapter."""

from __future__ import annotations

import pytest

from dataframe_adapter.domain.entities import InvalidDataError
from dataframe_adapter.infrastructure.adapters import JsonAdapter


def test_json_adapter_parses_valid_json_records() -> None:
    raw_bytes = b'[{"name": "Ana", "age": 30}, {"name": "Bob", "age": 25}]'
    dataset = JsonAdapter().load(raw_bytes)
    assert dataset.columns == ["name", "age"]
    assert dataset.rows == [["Ana", "30"], ["Bob", "25"]]
    assert dataset.source_format == "json"


def test_json_adapter_raises_on_malformed_json() -> None:
    with pytest.raises(InvalidDataError) as exc_info:
        JsonAdapter().load(b"{not valid json")
    assert exc_info.value.source_format == "json"


def test_json_adapter_raises_on_empty_bytes() -> None:
    with pytest.raises(InvalidDataError):
        JsonAdapter().load(b"")
