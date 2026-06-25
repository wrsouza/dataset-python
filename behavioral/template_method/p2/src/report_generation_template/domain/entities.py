"""Domain entities for the Report Generation Template."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class ReportRequest:
    """Input to a report generation run."""

    title: str
    rows: list[dict[str, Any]]


@dataclass(frozen=True)
class ReportResult:
    """Immutable outcome of generating a report."""

    report_id: str
    format_name: str
    content: str
    row_count: int
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
