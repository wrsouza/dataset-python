"""Unit tests for Composite containers (Row, Column, TabGroup).

Covers single-level grouping, multi-level nesting, count/depth computation
and the duplicate-child-name guard.
"""

from __future__ import annotations

import pytest

from src.dashboard.domain.entities import MetricCardData, TextBlockData
from src.dashboard.domain.exceptions import DuplicateChildComponentError
from src.dashboard.infrastructure.containers import Column, Row, TabGroup
from src.dashboard.infrastructure.widgets import MetricCard, TextBlock


def _card(name: str) -> MetricCard:
    return MetricCard(name, MetricCardData(label=name, value="1"))


class TestRow:
    def test_empty_row_has_zero_widgets_and_depth_one(self) -> None:
        row = Row("empty_row")
        assert row.count_widgets() == 0
        assert row.depth() == 1

    def test_row_with_leaves_counts_widgets(self) -> None:
        row = Row("kpi_row")
        row.add(_card("a"))
        row.add(_card("b"))
        assert row.count_widgets() == 2
        assert row.depth() == 2

    def test_render_includes_children_in_order(self) -> None:
        row = Row("kpi_row")
        row.add(_card("a"))
        row.add(_card("b"))
        rendered = row.render()
        assert rendered["type"] == "row"
        assert [child["name"] for child in rendered["children"]] == ["a", "b"]

    def test_add_duplicate_child_name_raises(self) -> None:
        row = Row("kpi_row")
        row.add(_card("a"))
        with pytest.raises(DuplicateChildComponentError):
            row.add(_card("a"))

    def test_children_property_returns_tuple(self) -> None:
        row = Row("kpi_row")
        row.add(_card("a"))
        assert row.children == (row.children[0],)


class TestColumn:
    def test_component_type_is_column(self) -> None:
        column = Column("left")
        assert column.component_type == "column"

    def test_nested_columns_increase_depth(self) -> None:
        inner = Column("inner")
        inner.add(_card("a"))
        outer = Column("outer")
        outer.add(inner)
        assert outer.depth() == 3
        assert outer.count_widgets() == 1


class TestTabGroup:
    def test_render_includes_tab_labels(self) -> None:
        tabs = TabGroup("main_tabs")
        tabs.add(Row("tab_one"))
        tabs.add(Row("tab_two"))
        rendered = tabs.render()
        assert rendered["tab_labels"] == ["tab_one", "tab_two"]

    def test_multi_level_nesting_three_deep(self) -> None:
        tabs = TabGroup("root_tabs")
        row = Row("row_inside_tab")
        column = Column("column_inside_row")
        column.add(_card("metric"))
        column.add(TextBlock("note", TextBlockData(content="x")))
        row.add(column)
        tabs.add(row)

        assert tabs.depth() == 4
        assert tabs.count_widgets() == 2

    def test_mixed_container_types_are_interchangeable(self) -> None:
        """LSP: any DashboardComponent (leaf or container) can be a child."""
        outer = Row("outer")
        outer.add(_card("leaf_child"))
        outer.add(Column("container_child"))
        assert outer.count_widgets() == 1
        assert outer.depth() == 2
