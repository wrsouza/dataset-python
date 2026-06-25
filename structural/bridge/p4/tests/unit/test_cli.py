"""Unit tests for the Typer CLI entry point."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from exporter.cli import app

runner = CliRunner()


def _write_data_file(tmp_path: Path) -> Path:
    data_file = tmp_path / "data.json"
    data_file.write_text(
        json.dumps(
            {
                "columns": ["product", "units"],
                "rows": [{"product": "Widget", "units": 10}],
            }
        ),
        encoding="utf-8",
    )
    return data_file


def test_list_formats_command() -> None:
    result = runner.invoke(app, ["list-formats"])

    assert result.exit_code == 0
    assert "csv" in result.stdout
    assert "excel" in result.stdout


def test_export_command_writes_csv_file(tmp_path: Path) -> None:
    data_file = _write_data_file(tmp_path)
    output_dir = tmp_path / "out"

    result = runner.invoke(
        app,
        [
            "export",
            "Sales Report",
            str(data_file),
            "--format",
            "csv",
            "--output-dir",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0
    assert (output_dir / "sales_report.csv").exists()


def test_export_command_rejects_unknown_format(tmp_path: Path) -> None:
    data_file = _write_data_file(tmp_path)

    result = runner.invoke(
        app, ["export", "Sales Report", str(data_file), "--format", "yaml"]
    )

    assert result.exit_code == 1
    assert "Unsupported format" in result.stdout
