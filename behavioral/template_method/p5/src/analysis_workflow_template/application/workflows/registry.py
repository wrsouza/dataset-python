"""Workflow registry — maps string keys to AnalysisWorkflow instances."""

from __future__ import annotations

from analysis_workflow_template.application.workflows.descriptive import (
    DescriptiveAnalysisWorkflow,
)
from analysis_workflow_template.application.workflows.trend import (
    TrendAnalysisWorkflow,
)
from analysis_workflow_template.domain.interfaces import AnalysisWorkflow

_WORKFLOW_MAP: dict[str, AnalysisWorkflow] = {
    "descriptive": DescriptiveAnalysisWorkflow(),
    "trend": TrendAnalysisWorkflow(),
}


class InvalidWorkflowError(Exception):
    def __init__(self, name: str) -> None:
        super().__init__(f"Unknown analysis workflow '{name}'")
        self.name = name


def get_workflow(name: str) -> AnalysisWorkflow:
    workflow = _WORKFLOW_MAP.get(name.lower())
    if workflow is None:
        raise InvalidWorkflowError(name)
    return workflow


def list_workflow_names() -> list[str]:
    return sorted(_WORKFLOW_MAP)
