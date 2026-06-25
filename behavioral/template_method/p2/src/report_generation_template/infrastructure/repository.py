"""In-memory repository for generated reports.

SRP: only stores/retrieves ReportResults by id — no rendering logic.
"""

from __future__ import annotations

from report_generation_template.domain.entities import ReportResult
from report_generation_template.domain.exceptions import ReportNotFoundError


class InMemoryReportRepository:
    def __init__(self) -> None:
        self._reports: dict[str, ReportResult] = {}

    def save(self, report: ReportResult) -> None:
        self._reports[report.report_id] = report

    def find_by_id(self, report_id: str) -> ReportResult:
        report = self._reports.get(report_id)
        if report is None:
            raise ReportNotFoundError(report_id)
        return report
