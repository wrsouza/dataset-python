"""Integration tests for the Typer CLI, using a real temporary JSON file."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from code_metrics_visitor.main import app

runner = CliRunner()


def _write_module(tmp_path: Path) -> Path:
    path = tmp_path / "module.json"
    path.write_text(
        json.dumps(
            {
                "name": "m",
                "functions": [
                    {
                        "name": "f",
                        "line_count": 10,
                        "branch_count": 2,
                        "has_docstring": True,
                    }
                ],
            }
        )
    )
    return path


def test_analyze_lines(tmp_path: Path) -> None:
    module_path = _write_module(tmp_path)

    result = runner.invoke(app, ["analyze", str(module_path), "--metric", "lines"])

    assert result.exit_code == 0
    assert "total_lines: 10" in result.stdout


def test_analyze_with_unknown_metric_exits_with_error(tmp_path: Path) -> None:
    module_path = _write_module(tmp_path)

    result = runner.invoke(app, ["analyze", str(module_path), "--metric", "unknown"])

    assert result.exit_code == 1
    assert "Unknown metric" in result.stdout


def test_list_metrics() -> None:
    result = runner.invoke(app, ["list-metrics"])

    assert result.exit_code == 0
    assert "lines" in result.stdout
    assert "complexity" in result.stdout
