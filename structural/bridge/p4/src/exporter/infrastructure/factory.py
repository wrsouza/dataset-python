"""Composition helper: resolves a FormatExporter by name.

This is the only place that knows about every concrete FormatExporter.
The CLI (composition root) calls this function; everything else in the
application depends solely on the FormatExporter/ReportExporter
abstractions.
"""

from __future__ import annotations

from exporter.domain.interfaces import FormatExporter
from exporter.infrastructure.csv_exporter import CsvFormatExporter
from exporter.infrastructure.excel_exporter import ExcelFormatExporter
from exporter.infrastructure.json_exporter import JsonFormatExporter
from exporter.infrastructure.xml_exporter import XmlFormatExporter

_EXPORTERS: dict[str, type[FormatExporter]] = {
    "csv": CsvFormatExporter,
    "json": JsonFormatExporter,
    "xml": XmlFormatExporter,
    "excel": ExcelFormatExporter,
}


def build_format_exporter(format_name: str) -> FormatExporter:
    """Instantiate the FormatExporter registered under format_name."""
    exporter_class = _EXPORTERS.get(format_name.lower())
    if exporter_class is None:
        supported = ", ".join(sorted(_EXPORTERS))
        raise ValueError(f"Unsupported format '{format_name}'. Supported: {supported}.")
    return exporter_class()
