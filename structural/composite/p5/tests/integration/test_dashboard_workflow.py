"""Integration test: full workflow JSON definition -> tree -> render data."""

from __future__ import annotations

from pathlib import Path

from src.dashboard.application.use_cases import (
    BuildDashboardTreeFromFileUseCase,
    ComputeTreeMetricsUseCase,
    RenderDashboardUseCase,
)


def test_full_definition_to_render_workflow(example_definition_path: Path) -> None:
    build_use_case = BuildDashboardTreeFromFileUseCase()
    render_use_case = RenderDashboardUseCase()
    metrics_use_case = ComputeTreeMetricsUseCase()

    tree = build_use_case.execute(example_definition_path)
    rendered = render_use_case.execute(tree)
    metrics = metrics_use_case.execute(tree)

    assert rendered["type"] == "tab_group"
    assert rendered["name"] == "main_dashboard"
    assert rendered["tab_labels"] == ["overview_tab", "details_tab"]

    assert metrics.widget_count == 7
    assert metrics.depth == 4
    assert metrics.container_count > 0


def test_rendered_tree_is_fully_json_serializable(
    example_definition_path: Path,
) -> None:
    import json

    build_use_case = BuildDashboardTreeFromFileUseCase()
    render_use_case = RenderDashboardUseCase()

    tree = build_use_case.execute(example_definition_path)
    rendered = render_use_case.execute(tree)

    serialized = json.dumps(rendered)
    assert json.loads(serialized) == rendered


def test_leaf_widgets_are_reachable_inside_nested_tabs(
    example_definition_path: Path,
) -> None:
    build_use_case = BuildDashboardTreeFromFileUseCase()
    render_use_case = RenderDashboardUseCase()

    tree = build_use_case.execute(example_definition_path)
    rendered = render_use_case.execute(tree)

    overview_children = rendered["children"][0]["children"]
    leaf_names = {child["name"] for child in overview_children}
    assert "revenue_chart" in leaf_names
    assert "overview_note" in leaf_names
