"""Unit tests for ParquetAdapter."""

from __future__ import annotations

import io

import pandas as pd
import pytest

from dataframe_adapter.domain.entities import InvalidDataError
from dataframe_adapter.infrastructure.adapters import ParquetAdapter


def _build_parquet_bytes() -> bytes:
    dataframe = pd.DataFrame({"name": ["Ana", "Bob"], "age": [30, 25]})
    buffer = io.BytesIO()
    dataframe.to_parquet(buffer, index=False)
    return buffer.getvalue()


def test_parquet_adapter_parses_valid_parquet() -> None:
    raw_bytes = _build_parquet_bytes()
    dataset = ParquetAdapter().load(raw_bytes)
    assert dataset.columns == ["name", "age"]
    assert dataset.rows == [["Ana", "30"], ["Bob", "25"]]
    assert dataset.source_format == "parquet"


def test_parquet_adapter_raises_on_corrupted_bytes() -> None:
    with pytest.raises(InvalidDataError) as exc_info:
        ParquetAdapter().load(b"not a real parquet file")
    assert exc_info.value.source_format == "parquet"


def test_parquet_adapter_raises_on_empty_bytes() -> None:
    with pytest.raises(InvalidDataError):
        ParquetAdapter().load(b"")
