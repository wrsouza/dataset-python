"""Integration-style test exercising every registered workflow, mirroring
how the Streamlit app wires the selectbox to the registry."""

from __future__ import annotations

from analysis_workflow_template.application.workflows.registry import (
    get_workflow,
    list_workflow_names,
)


def test_every_registered_workflow_produces_a_report() -> None:
    dataset = [10.0, 12.0, 11.0, 13.0, 90.0]

    for name in list_workflow_names():
        report = get_workflow(name).run(dataset)

        assert report.workflow_name == name
        assert report.interpretation
