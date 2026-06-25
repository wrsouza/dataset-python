"""Unit tests for domain entities."""

from __future__ import annotations

from exporter.domain.entities import ExportResult, Report, ReportColumn, ReportRow


def test_report_column_names_preserves_order() -> None:
    columns = [ReportColumn(name="a", label="A"), ReportColumn(name="b", label="B")]
    report = Report(title="T", columns=columns, rows=[])

    assert report.column_names() == ["a", "b"]


def test_report_defaults_to_empty_rows() -> None:
    report = Report(title="Empty", columns=[ReportColumn(name="x", label="X")])

    assert report.rows == []


def test_report_row_holds_values() -> None:
    row = ReportRow(values={"a": 1, "b": "text"})

    assert row.values["a"] == 1
    assert row.values["b"] == "text"


def test_export_result_to_dict() -> None:
    result = ExportResult(destination="/tmp/out.csv", format_name="CSV", byte_size=42)

    assert result.to_dict() == {
        "destination": "/tmp/out.csv",
        "format_name": "CSV",
        "byte_size": 42,
    }
