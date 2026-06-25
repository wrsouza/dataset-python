"""Unit tests for the workflow registry."""

from __future__ import annotations

import pytest

from analysis_workflow_template.application.workflows.descriptive import (
    DescriptiveAnalysisWorkflow,
)
from analysis_workflow_template.application.workflows.registry import (
    InvalidWorkflowError,
    get_workflow,
    list_workflow_names,
)


def test_get_workflow_resolves_descriptive() -> None:
    workflow = get_workflow("descriptive")

    assert isinstance(workflow, DescriptiveAnalysisWorkflow)


def test_get_workflow_is_case_insensitive() -> None:
    workflow = get_workflow("TREND")

    assert workflow.get_name() == "trend"


def test_get_workflow_raises_for_unknown_name() -> None:
    with pytest.raises(InvalidWorkflowError):
        get_workflow("unknown")


def test_list_workflow_names_includes_all_registered() -> None:
    assert list_workflow_names() == ["descriptive", "trend"]
