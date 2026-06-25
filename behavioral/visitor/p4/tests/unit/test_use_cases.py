"""Unit tests for AnalyzeModuleUseCase, using a real temporary JSON file."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from code_metrics_visitor.application.use_cases import (
    AnalyzeModuleInput,
    AnalyzeModuleUseCase,
)
from code_metrics_visitor.domain.exceptions import InvalidMetricError


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


def test_execute_runs_the_requested_metric(tmp_path: Path) -> None:
    module_path = _write_module(tmp_path)
    use_case = AnalyzeModuleUseCase()

    result = use_case.execute(
        AnalyzeModuleInput(module_path=module_path, metric_name="lines")
    )

    assert result.data["total_lines"] == 10


def test_execute_raises_for_unknown_metric(tmp_path: Path) -> None:
    module_path = _write_module(tmp_path)
    use_case = AnalyzeModuleUseCase()

    with pytest.raises(InvalidMetricError):
        use_case.execute(
            AnalyzeModuleInput(module_path=module_path, metric_name="unknown")
        )
