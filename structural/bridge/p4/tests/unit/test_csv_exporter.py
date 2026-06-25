"""Unit tests for CsvFormatExporter."""

from __future__ import annotations

from exporter.domain.entities import Report
from exporter.infrastructure.csv_exporter import CsvFormatExporter


def test_serialize_writes_header_and_rows(sample_report: Report) -> None:
    exporter = CsvFormatExporter()

    output = exporter.serialize(sample_report).decode("utf-8")

    assert "product,units" in output
    assert "Widget,10" in output
    assert "Gadget,5" in output


def test_format_metadata() -> None:
    exporter = CsvFormatExporter()

    assert exporter.file_extension() == "csv"
    assert exporter.format_name() == "CSV"
