"""Unit tests for domain entities and exceptions."""

from __future__ import annotations

from dataframe_adapter.domain.entities import (
    InvalidDataError,
    ParsedDataset,
    UnsupportedFormatError,
)


def test_parsed_dataset_computes_row_count() -> None:
    dataset = ParsedDataset(
        columns=["a", "b"], rows=[["1", "2"], ["3", "4"]], source_format="csv"
    )
    assert dataset.row_count == 2


def test_parsed_dataset_to_csv_text_basic() -> None:
    dataset = ParsedDataset(
        columns=["name", "age"], rows=[["Ana", "30"]], source_format="json"
    )
    assert dataset.to_csv_text() == "name,age\nAna,30\n"


def test_parsed_dataset_to_csv_text_escapes_comma_and_quotes() -> None:
    dataset = ParsedDataset(
        columns=["note"], rows=[['has, comma and "quote"']], source_format="csv"
    )
    csv_text = dataset.to_csv_text()
    assert csv_text == 'note\n"has, comma and ""quote"""\n'


def test_parsed_dataset_to_csv_text_escapes_newline() -> None:
    dataset = ParsedDataset(columns=["x"], rows=[["line1\nline2"]], source_format="csv")
    assert dataset.to_csv_text() == 'x\n"line1\nline2"\n'


def test_parsed_dataset_empty_rows() -> None:
    dataset = ParsedDataset(columns=["a"], rows=[], source_format="csv")
    assert dataset.row_count == 0
    assert dataset.to_csv_text() == "a\n"


def test_unsupported_format_error_message() -> None:
    error = UnsupportedFormatError("data.xml")
    assert "data.xml" in str(error)
    assert error.filename == "data.xml"


def test_invalid_data_error_message() -> None:
    error = InvalidDataError("csv", "linha malformada")
    assert "csv" in str(error)
    assert "linha malformada" in str(error)
    assert error.source_format == "csv"
    assert error.reason == "linha malformada"
