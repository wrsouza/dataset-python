"""Abstraction side of the Bridge pattern plus the use case that drives it.

`ReportExporter` is the Abstraction: it exposes a stable, high-level API
(`export`) to client code (the CLI) while delegating the format-specific
encoding to whichever `FormatExporter` (Implementor) was injected into it.
Adding a new export format never requires touching `ReportExporter` or the
use case below — only a new `FormatExporter` implementation.
"""

from __future__ import annotations

from pathlib import Path

from exporter.domain.entities import ExportResult, Report
from exporter.domain.interfaces import FormatExporter


class UnsupportedReportError(Exception):
    """Raised when a report cannot be exported (e.g. empty columns)."""


class ReportExporter:
    """Bridge Abstraction: exports a Report using an injected FormatExporter."""

    def __init__(self, format_exporter: FormatExporter) -> None:
        self._format_exporter = format_exporter

    def export(self, report: Report) -> bytes:
        """Delegate encoding to the format implementor and return raw bytes."""
        if not report.columns:
            raise UnsupportedReportError("Report must declare at least one column.")
        return self._format_exporter.serialize(report)

    def format_name(self) -> str:
        """Expose the active format's name without leaking its type."""
        return self._format_exporter.format_name()

    def file_extension(self) -> str:
        """Expose the active format's file extension."""
        return self._format_exporter.file_extension()


class ExportReportUseCase:
    """Use case: export a report to disk using the configured ReportExporter."""

    def __init__(self, exporter: ReportExporter) -> None:
        self._exporter = exporter

    def execute(self, report: Report, output_dir: Path) -> ExportResult:
        """Export the report and write it under output_dir, returning metadata."""
        payload = self._exporter.export(report)
        output_dir.mkdir(parents=True, exist_ok=True)
        file_name = f"{_slugify(report.title)}.{self._exporter.file_extension()}"
        destination = output_dir / file_name
        destination.write_bytes(payload)
        return ExportResult(
            destination=str(destination),
            format_name=self._exporter.format_name(),
            byte_size=len(payload),
        )


def _slugify(title: str) -> str:
    """Turn a report title into a filesystem-safe, lowercase slug."""
    return "_".join(title.lower().split())
