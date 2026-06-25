"""Unit tests for the FormatExporter resolution factory."""

from __future__ import annotations

import pytest

from exporter.infrastructure.csv_exporter import CsvFormatExporter
from exporter.infrastructure.excel_exporter import ExcelFormatExporter
from exporter.infrastructure.factory import build_format_exporter
from exporter.infrastructure.json_exporter import JsonFormatExporter
from exporter.infrastructure.xml_exporter import XmlFormatExporter


@pytest.mark.parametrize(
    ("format_name", "expected_type"),
    [
        ("csv", CsvFormatExporter),
        ("JSON", JsonFormatExporter),
        ("Xml", XmlFormatExporter),
        ("excel", ExcelFormatExporter),
    ],
)
def test_build_format_exporter_resolves_known_formats(
    format_name: str, expected_type: type
) -> None:
    exporter = build_format_exporter(format_name)

    assert isinstance(exporter, expected_type)


def test_build_format_exporter_rejects_unknown_format() -> None:
    with pytest.raises(ValueError, match="Unsupported format"):
        build_format_exporter("yaml")
