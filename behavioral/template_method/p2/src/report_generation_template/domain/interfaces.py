"""AbstractClass for the Template Method pattern — ReportGenerator.

Template Method defines the skeleton of the report-rendering algorithm
in `generate()`. Subclasses override `format_header()`, `format_row()`,
and `get_format_name()` without changing the overall flow.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Any

from report_generation_template.domain.entities import ReportResult


class ReportGenerator(ABC):
    """AbstractClass: defines the `generate()` template method.

    Fixed steps (always run in this order):
        1. format_header   — abstract, subclass-specific
        2. format_row       — abstract, subclass-specific (called per row)
        3. format_summary   — concrete, shared row-count line
        4. assemble          — concrete, joins header+rows+summary

    Hook:
        include_summary() — returns True (default) to append the row-count
                             summary line; subclasses may override to skip it.
    """

    @abstractmethod
    def format_header(self, title: str) -> str:
        """Render the report's header/title section."""

    @abstractmethod
    def format_row(self, row: dict[str, Any]) -> str:
        """Render a single data row."""

    @abstractmethod
    def get_format_name(self) -> str:
        """Return the canonical name of this report format."""

    # ── Hook ────────────────────────────────────────────────────────────────────

    def include_summary(self) -> bool:
        """Whether to append the shared row-count summary line."""
        return True

    # ── Concrete steps ──────────────────────────────────────────────────────────

    def format_summary(self, row_count: int) -> str:
        return f"Total records: {row_count}"

    def assemble(self, header: str, rows: list[str], summary: str | None) -> str:
        parts = [header, *rows]
        if summary is not None:
            parts.append(summary)
        return "\n".join(parts)

    # ── Template Method ─────────────────────────────────────────────────────────

    def generate(self, title: str, rows: list[dict[str, Any]]) -> ReportResult:
        """Template method — defines the fixed report-rendering algorithm."""
        header = self.format_header(title)
        rendered_rows = [self.format_row(row) for row in rows]
        summary = self.format_summary(len(rows)) if self.include_summary() else None
        content = self.assemble(header, rendered_rows, summary)

        return ReportResult(
            report_id=str(uuid.uuid4()),
            format_name=self.get_format_name(),
            content=content,
            row_count=len(rows),
        )
