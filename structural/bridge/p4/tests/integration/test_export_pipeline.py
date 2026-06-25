"""Integration tests: full Bridge pipeline against every real format."""

from __future__ import annotations

from pathlib import Path

import pytest

from exporter.application.use_cases import ExportReportUseCase, ReportExporter
from exporter.domain.entities import Report
from exporter.infrastructure.factory import build_format_exporter

ALL_FORMATS = ["csv", "json", "xml", "excel"]


@pytest.mark.parametrize("format_name", ALL_FORMATS)
def test_export_pipeline_writes_real_file_for_each_format(
    tmp_path: Path, sample_report: Report, format_name: str
) -> None:
    format_exporter = build_format_exporter(format_name)
    exporter = ReportExporter(format_exporter)
    use_case = ExportReportUseCase(exporter)

    result = use_case.execute(sample_report, tmp_path)

    destination = Path(result.destination)
    assert destination.exists()
    assert destination.stat().st_size > 0
    assert result.byte_size == destination.stat().st_size


def test_export_pipeline_creates_output_dir_if_missing(
    tmp_path: Path, sample_report: Report
) -> None:
    nested_dir = tmp_path / "nested" / "exports"
    exporter = ReportExporter(build_format_exporter("csv"))
    use_case = ExportReportUseCase(exporter)

    use_case.execute(sample_report, nested_dir)

    assert nested_dir.exists()
