"""Domain exceptions for the Report Generation Template."""

from __future__ import annotations


class InvalidFormatError(Exception):
    """Raised when a report format name is not registered."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Unknown report format '{name}'")
        self.name = name


class ReportNotFoundError(Exception):
    """Raised when a previously generated report cannot be found."""

    def __init__(self, report_id: str) -> None:
        super().__init__(f"Report '{report_id}' not found")
        self.report_id = report_id
