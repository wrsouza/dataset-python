"""JSON concrete implementor for the Export Format Bridge."""

from __future__ import annotations

import json

from exporter.domain.entities import Report
from exporter.domain.interfaces import FormatExporter


class JsonFormatExporter(FormatExporter):
    """Encodes a Report as a JSON object with title, columns and rows."""

    def serialize(self, report: Report) -> bytes:
        payload = {
            "title": report.title,
            "columns": report.column_names(),
            "rows": [row.values for row in report.rows],
        }
        return json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")

    def file_extension(self) -> str:
        return "json"

    def format_name(self) -> str:
        return "JSON"
