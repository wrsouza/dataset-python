"""Integration tests: full flow upload bytes -> detect -> parse -> normalize CSV."""

from __future__ import annotations

import io

import pandas as pd

from dataframe_adapter.application.use_cases import (
    AdapterFactory,
    NormalizeToCsvUseCase,
)


def _use_case() -> NormalizeToCsvUseCase:
    return NormalizeToCsvUseCase(AdapterFactory())


def test_full_flow_csv_to_normalized_csv() -> None:
    raw_bytes = b"name,age,city\nAna,30,SP\nBob,25,RJ\n"
    csv_text = _use_case().execute(raw_bytes, "uploaded.csv")
    assert csv_text == "name,age,city\nAna,30,SP\nBob,25,RJ\n"


def test_full_flow_json_to_normalized_csv() -> None:
    raw_bytes = (
        b'[{"name": "Ana", "age": 30, "city": "SP"}, '
        b'{"name": "Bob", "age": 25, "city": "RJ"}]'
    )
    csv_text = _use_case().execute(raw_bytes, "uploaded.json")
    assert csv_text == "name,age,city\nAna,30,SP\nBob,25,RJ\n"


def test_full_flow_parquet_to_normalized_csv() -> None:
    dataframe = pd.DataFrame(
        {"name": ["Ana", "Bob"], "age": [30, 25], "city": ["SP", "RJ"]}
    )
    buffer = io.BytesIO()
    dataframe.to_parquet(buffer, index=False)

    csv_text = _use_case().execute(buffer.getvalue(), "uploaded.parquet")
    assert csv_text == "name,age,city\nAna,30,SP\nBob,25,RJ\n"


def test_full_flow_preserves_row_and_column_counts_across_formats() -> None:
    csv_bytes = b"a,b\n1,2\n3,4\n5,6\n"
    json_bytes = b'[{"a": 1, "b": 2}, {"a": 3, "b": 4}, {"a": 5, "b": 6}]'

    use_case = _use_case()
    csv_dataset = use_case.parse(csv_bytes, "data.csv")
    json_dataset = use_case.parse(json_bytes, "data.json")

    assert csv_dataset.row_count == json_dataset.row_count == 3
    assert csv_dataset.columns == json_dataset.columns == ["a", "b"]
