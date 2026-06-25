"""Unit tests for ReportExporter (Abstraction) and ExportReportUseCase."""

from __future__ import annotations

from pathlib import Path

import pytest

from exporter.application.use_cases import (
    ExportReportUseCase,
    ReportExporter,
    UnsupportedReportError,
)
from exporter.domain.entities import Report, ReportColumn
from exporter.domain.interfaces import FormatExporter


class FakeFormatExporter(FormatExporter):
    """In-memory test double standing in for a real format implementor."""

    def serialize(self, report: Report) -> bytes:
        return f"fake:{report.title}".encode()

    def file_extension(self) -> str:
        return "fake"

    def format_name(self) -> str:
        return "Fake"


def test_report_exporter_delegates_to_format_exporter(sample_report: Report) -> None:
    exporter = ReportExporter(FakeFormatExporter())

    payload = exporter.export(sample_report)

    assert payload == b"fake:Sales Report"


def test_report_exporter_exposes_format_metadata() -> None:
    exporter = ReportExporter(FakeFormatExporter())

    assert exporter.format_name() == "Fake"
    assert exporter.file_extension() == "fake"


def test_report_exporter_rejects_report_without_columns() -> None:
    exporter = ReportExporter(FakeFormatExporter())
    empty_report = Report(title="Empty", columns=[])

    with pytest.raises(UnsupportedReportError):
        exporter.export(empty_report)


def test_export_report_use_case_writes_file(
    tmp_path: Path, sample_report: Report
) -> None:
    exporter = ReportExporter(FakeFormatExporter())
    use_case = ExportReportUseCase(exporter)

    result = use_case.execute(sample_report, tmp_path)

    destination = Path(result.destination)
    assert destination.exists()
    assert destination.read_bytes() == b"fake:Sales Report"
    assert result.format_name == "Fake"
    assert result.byte_size == len(b"fake:Sales Report")


def test_export_report_use_case_slugifies_title(tmp_path: Path) -> None:
    exporter = ReportExporter(FakeFormatExporter())
    use_case = ExportReportUseCase(exporter)
    report = Report(
        title="Q1 Sales Report", columns=[ReportColumn(name="x", label="X")]
    )

    result = use_case.execute(report, tmp_path)

    assert result.destination.endswith("q1_sales_report.fake")
