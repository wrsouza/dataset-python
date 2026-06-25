"""CSVReportGenerator — ConcreteClass rendering comma-separated rows."""

from __future__ import annotations

from typing import Any

from report_generation_template.domain.interfaces import ReportGenerator


class CSVReportGenerator(ReportGenerator):
    def format_header(self, title: str) -> str:
        return f"# {title}"

    def format_row(self, row: dict[str, Any]) -> str:
        return ",".join(str(value) for value in row.values())

    def get_format_name(self) -> str:
        return "csv"
