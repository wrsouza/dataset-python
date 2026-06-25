"""Unit tests for DescriptiveAnalysisWorkflow."""

from __future__ import annotations

from analysis_workflow_template.application.workflows.descriptive import (
    DescriptiveAnalysisWorkflow,
)


def test_run_computes_statistics_and_interpretation() -> None:
    report = DescriptiveAnalysisWorkflow().run([1.0, 2.0, 3.0, 4.0, 100.0])

    assert report.workflow_name == "descriptive"
    assert report.statistics["count"] == 5
    assert "averaging" in report.interpretation


def test_run_flags_outliers_by_default() -> None:
    dataset = [10.0, 11.0, 9.0, 10.0, 10.0, 11.0, 9.0, 10.0, 10.0, 1000.0]

    report = DescriptiveAnalysisWorkflow().run(dataset)

    assert 1000.0 in report.outliers


def test_run_with_empty_dataset() -> None:
    report = DescriptiveAnalysisWorkflow().run([])

    assert report.statistics["count"] == 0
    assert report.interpretation == "No data to describe."
    assert report.outliers == []
