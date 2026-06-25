"""HTMLReportGenerator — ConcreteClass rendering an HTML table."""

from __future__ import annotations

from typing import Any

from report_generation_template.domain.interfaces import ReportGenerator


class HTMLReportGenerator(ReportGenerator):
    def format_header(self, title: str) -> str:
        return f"<h1>{title}</h1>\n<table>"

    def format_row(self, row: dict[str, Any]) -> str:
        cells = "".join(f"<td>{value}</td>" for value in row.values())
        return f"<tr>{cells}</tr>"

    def get_format_name(self) -> str:
        return "html"

    # ── Concrete step override ──────────────────────────────────────────────────

    def assemble(self, header: str, rows: list[str], summary: str | None) -> str:
        body = "\n".join(rows)
        closing = "</table>"
        if summary is not None:
            closing += f"\n<p>{summary}</p>"
        return f"{header}\n{body}\n{closing}"
