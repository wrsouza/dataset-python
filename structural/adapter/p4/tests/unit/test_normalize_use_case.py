"""Unit tests for NormalizeToCsvUseCase."""

from __future__ import annotations

import pytest

from dataframe_adapter.application.use_cases import (
    AdapterFactory,
    NormalizeToCsvUseCase,
)
from dataframe_adapter.domain.entities import UnsupportedFormatError


def test_normalize_use_case_parses_csv_and_exports_csv() -> None:
    use_case = NormalizeToCsvUseCase(AdapterFactory())
    raw_bytes = b"name,age\nAna,30\n"
    csv_text = use_case.execute(raw_bytes, "people.csv")
    assert csv_text == "name,age\nAna,30\n"


def test_normalize_use_case_parses_json_and_exports_csv() -> None:
    use_case = NormalizeToCsvUseCase(AdapterFactory())
    raw_bytes = b'[{"name": "Ana", "age": 30}]'
    csv_text = use_case.execute(raw_bytes, "people.json")
    assert csv_text == "name,age\nAna,30\n"


def test_normalize_use_case_raises_for_unsupported_format() -> None:
    use_case = NormalizeToCsvUseCase(AdapterFactory())
    with pytest.raises(UnsupportedFormatError):
        use_case.execute(b"<root/>", "people.xml")


def test_normalize_use_case_parse_returns_dataset() -> None:
    use_case = NormalizeToCsvUseCase(AdapterFactory())
    dataset = use_case.parse(b"a,b\n1,2\n", "file.csv")
    assert dataset.columns == ["a", "b"]
    assert dataset.source_format == "csv"
