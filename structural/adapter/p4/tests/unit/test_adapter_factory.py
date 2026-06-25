"""Unit tests for AdapterFactory."""

from __future__ import annotations

import pytest

from dataframe_adapter.application.use_cases import AdapterFactory
from dataframe_adapter.domain.entities import UnsupportedFormatError
from dataframe_adapter.infrastructure.adapters import (
    CsvAdapter,
    JsonAdapter,
    ParquetAdapter,
)


@pytest.mark.parametrize(
    ("filename", "expected_type"),
    [
        ("data.csv", CsvAdapter),
        ("data.json", JsonAdapter),
        ("data.parquet", ParquetAdapter),
        ("DATA.CSV", CsvAdapter),
    ],
)
def test_factory_returns_correct_adapter(filename: str, expected_type: type) -> None:
    adapter = AdapterFactory().create_for_filename(filename)
    assert isinstance(adapter, expected_type)


def test_factory_raises_for_unsupported_extension() -> None:
    with pytest.raises(UnsupportedFormatError) as exc_info:
        AdapterFactory().create_for_filename("data.xml")
    assert exc_info.value.filename == "data.xml"


def test_factory_raises_for_missing_extension() -> None:
    with pytest.raises(UnsupportedFormatError):
        AdapterFactory().create_for_filename("data")
