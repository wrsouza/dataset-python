"""Unit tests for the application-layer use cases."""

from __future__ import annotations

from pathlib import Path

from src.dashboard.application.use_cases import (
    BuildDashboardTreeFromFileUseCase,
    BuildDashboardTreeFromJsonUseCase,
    BuildDashboardTreeUseCase,
    ComputeTreeMetricsUseCase,
    RenderDashboardUseCase,
)
from src.dashboard.domain.entities import MetricCardData
from src.dashboard.infrastructure.containers import Column, Row, TabGroup
from src.dashboard.infrastructure.widgets import MetricCard


class TestBuildDashboardTreeUseCase:
    def test_builds_tree_from_dict(self) -> None:
        use_case = BuildDashboardTreeUseCase()
        tree = use_case.execute(
            {"type": "metric_card", "name": "m", "props": {"value": "1"}}
        )
        assert isinstance(tree, MetricCard)


class TestBuildDashboardTreeFromJsonUseCase:
    def test_builds_tree_from_json_string(self) -> None:
        use_case = BuildDashboardTreeFromJsonUseCase()
        tree = use_case.execute('{"type": "row", "name": "r", "children": []}')
        assert isinstance(tree, Row)


class TestBuildDashboardTreeFromFileUseCase:
    def test_builds_tree_from_example_file(self, example_definition_path: Path) -> None:
        use_case = BuildDashboardTreeFromFileUseCase()
        tree = use_case.execute(example_definition_path)
        assert tree.component_type == "tab_group"


class TestRenderDashboardUseCase:
    def test_returns_plain_dict_structure(self) -> None:
        row = Row("r")
        row.add(MetricCard("m", MetricCardData(label="M", value="1")))
        use_case = RenderDashboardUseCase()
        rendered = use_case.execute(row)
        assert rendered["type"] == "row"
        assert rendered["children"][0]["type"] == "metric_card"


class TestComputeTreeMetricsUseCase:
    def test_computes_metrics_for_nested_tree(self) -> None:
        tabs = TabGroup("tabs")
        column = Column("col")
        column.add(MetricCard("a", MetricCardData(label="A", value="1")))
        column.add(MetricCard("b", MetricCardData(label="B", value="2")))
        tabs.add(column)

        use_case = ComputeTreeMetricsUseCase()
        metrics = use_case.execute(tabs)

        assert metrics.widget_count == 2
        assert metrics.depth == 3
        assert metrics.container_count == 2

    def test_single_leaf_tree_has_zero_containers(self) -> None:
        leaf = MetricCard("solo", MetricCardData(label="S", value="1"))
        use_case = ComputeTreeMetricsUseCase()
        metrics = use_case.execute(leaf)

        assert metrics.widget_count == 1
        assert metrics.depth == 1
        assert metrics.container_count == 0
