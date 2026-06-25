"""Unit tests for TrendAnalysisWorkflow."""

from __future__ import annotations

from analysis_workflow_template.application.workflows.trend import (
    TrendAnalysisWorkflow,
)


def test_run_detects_upward_trend() -> None:
    report = TrendAnalysisWorkflow().run([1.0, 2.0, 3.0, 4.0])

    assert "upward" in report.interpretation


def test_run_detects_downward_trend() -> None:
    report = TrendAnalysisWorkflow().run([4.0, 3.0, 2.0, 1.0])

    assert "downward" in report.interpretation


def test_run_skips_outlier_detection_via_hook() -> None:
    report = TrendAnalysisWorkflow().run([1.0, 2.0, 3.0, 100.0])

    assert report.outliers == []


def test_run_with_fewer_than_two_points() -> None:
    report = TrendAnalysisWorkflow().run([1.0])

    assert report.statistics["count"] == 0
    assert report.interpretation == "Not enough points to estimate a trend."


def test_get_name() -> None:
    assert TrendAnalysisWorkflow().get_name() == "trend"
