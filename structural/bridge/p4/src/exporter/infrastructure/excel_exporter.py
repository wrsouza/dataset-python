"""Excel concrete implementor for the Export Format Bridge.

Uses openpyxl directly (no pandas/numpy) to keep the dependency surface
small, per the project's stack conventions.
"""

from __future__ import annotations

import io

from openpyxl import Workbook

from exporter.domain.entities import Report
from exporter.domain.interfaces import FormatExporter


class ExcelFormatExporter(FormatExporter):
    """Encodes a Report as an .xlsx workbook using openpyxl."""

    def serialize(self, report: Report) -> bytes:
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = report.title[:31] or "Report"
        column_names = report.column_names()
        worksheet.append(column_names)
        for row in report.rows:
            worksheet.append([row.values.get(name) for name in column_names])
        buffer = io.BytesIO()
        workbook.save(buffer)
        return buffer.getvalue()

    def file_extension(self) -> str:
        return "xlsx"

    def format_name(self) -> str:
        return "Excel"
