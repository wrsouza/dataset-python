"""CSV concrete implementor for the Export Format Bridge."""

from __future__ import annotations

import csv
import io

from exporter.domain.entities import Report
from exporter.domain.interfaces import FormatExporter


class CsvFormatExporter(FormatExporter):
    """Encodes a Report as RFC 4180 CSV using the stdlib csv module."""

    def serialize(self, report: Report) -> bytes:
        buffer = io.StringIO()
        column_names = report.column_names()
        writer = csv.DictWriter(buffer, fieldnames=column_names)
        writer.writeheader()
        for row in report.rows:
            writer.writerow(row.values)
        return buffer.getvalue().encode("utf-8")

    def file_extension(self) -> str:
        return "csv"

    def format_name(self) -> str:
        return "CSV"
