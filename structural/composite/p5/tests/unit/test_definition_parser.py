"""Unit tests for building a DashboardComponent tree from definitions."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.dashboard.domain.exceptions import (
    DashboardDefinitionError,
    UnknownComponentTypeError,
)
from src.dashboard.infrastructure.containers import Column, Row, TabGroup
from src.dashboard.infrastructure.definition_parser import (
    build_component_tree,
    load_definition_from_file,
    load_definition_from_json,
)
from src.dashboard.infrastructure.widgets import MetricCard


class TestBuildComponentTree:
    def test_builds_leaf_from_definition(self) -> None:
        component = build_component_tree(
            {
                "type": "metric_card",
                "name": "revenue_card",
                "props": {"label": "Receita", "value": "100"},
            }
        )
        assert isinstance(component, MetricCard)

    def test_builds_single_level_container(self) -> None:
        component = build_component_tree(
            {
                "type": "row",
                "name": "kpi_row",
                "children": [
                    {
                        "type": "metric_card",
                        "name": "a",
                        "props": {"label": "A", "value": "1"},
                    }
                ],
            }
        )
        assert isinstance(component, Row)
        assert component.count_widgets() == 1

    def test_builds_multi_level_nested_tree(self) -> None:
        component = build_component_tree(
            {
                "type": "tab_group",
                "name": "tabs",
                "children": [
                    {
                        "type": "column",
                        "name": "tab1",
                        "children": [
                            {
                                "type": "row",
                                "name": "inner_row",
                                "children": [
                                    {
                                        "type": "metric_card",
                                        "name": "m1",
                                        "props": {"label": "M1", "value": "1"},
                                    },
                                    {
                                        "type": "metric_card",
                                        "name": "m2",
                                        "props": {"label": "M2", "value": "2"},
                                    },
                                ],
                            }
                        ],
                    }
                ],
            }
        )
        assert isinstance(component, TabGroup)
        assert component.count_widgets() == 2
        assert component.depth() == 4

    def test_missing_name_raises(self) -> None:
        with pytest.raises(DashboardDefinitionError):
            build_component_tree({"type": "metric_card", "props": {}})

    def test_missing_type_raises(self) -> None:
        with pytest.raises(DashboardDefinitionError):
            build_component_tree({"name": "x"})

    def test_container_children_not_list_raises(self) -> None:
        with pytest.raises(DashboardDefinitionError):
            build_component_tree({"type": "row", "name": "r", "children": "bad"})

    def test_leaf_props_not_mapping_raises(self) -> None:
        with pytest.raises(DashboardDefinitionError):
            build_component_tree({"type": "metric_card", "name": "m", "props": "bad"})

    def test_unknown_leaf_type_raises(self) -> None:
        with pytest.raises(UnknownComponentTypeError):
            build_component_tree({"type": "unknown", "name": "x"})


class TestColumnComponentType:
    def test_column_definition_builds_column_instance(self) -> None:
        component = build_component_tree(
            {"type": "column", "name": "col", "children": []}
        )
        assert isinstance(component, Column)


class TestLoadDefinitionFromJson:
    def test_parses_valid_json(self) -> None:
        definition = load_definition_from_json('{"type": "row", "name": "r"}')
        assert definition == {"type": "row", "name": "r"}

    def test_invalid_json_raises(self) -> None:
        with pytest.raises(DashboardDefinitionError):
            load_definition_from_json("{not valid json")

    def test_non_mapping_root_raises(self) -> None:
        with pytest.raises(DashboardDefinitionError):
            load_definition_from_json("[1, 2, 3]")


class TestLoadDefinitionFromFile:
    def test_loads_bundled_example(self, example_definition_path: Path) -> None:
        definition = load_definition_from_file(example_definition_path)
        assert definition["type"] == "tab_group"
        assert definition["name"] == "main_dashboard"
