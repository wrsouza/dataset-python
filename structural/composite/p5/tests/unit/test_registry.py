"""Unit tests for the widget-builder registry (OCP extension point)."""

from __future__ import annotations

import pytest

from src.dashboard.domain.entities import MetricCardData
from src.dashboard.domain.exceptions import UnknownComponentTypeError
from src.dashboard.infrastructure import registry as registry_module
from src.dashboard.infrastructure.registry import (
    build_leaf_widget,
    register_widget_builder,
    registered_widget_types,
)
from src.dashboard.infrastructure.widgets import ChartWidget, MetricCard, TextBlock


class TestBuildLeafWidget:
    def test_builds_metric_card(self) -> None:
        widget = build_leaf_widget(
            "metric_card", "revenue", {"label": "Receita", "value": "100"}
        )
        assert isinstance(widget, MetricCard)
        assert widget.render()["label"] == "Receita"

    def test_builds_text_block(self) -> None:
        widget = build_leaf_widget("text_block", "note", {"content": "Olá"})
        assert isinstance(widget, TextBlock)

    def test_builds_chart(self) -> None:
        widget = build_leaf_widget("chart", "chart1", {"chart_type": "bar"})
        assert isinstance(widget, ChartWidget)

    def test_unknown_type_raises(self) -> None:
        with pytest.raises(UnknownComponentTypeError):
            build_leaf_widget("unknown_widget", "x", {})

    def test_metric_card_defaults_label_to_name(self) -> None:
        widget = build_leaf_widget("metric_card", "fallback_name", {"value": "1"})
        assert widget.render()["label"] == "fallback_name"


class TestRegisteredWidgetTypes:
    def test_default_types_are_registered(self) -> None:
        types = registered_widget_types()
        assert "metric_card" in types
        assert "text_block" in types
        assert "chart" in types

    def test_register_new_widget_type_extends_without_modifying_existing(self) -> None:
        """OCP: a brand-new widget type can be added via registration."""

        def _build_divider(name: str, props: dict[str, object]) -> MetricCard:
            del props
            return MetricCard(name, MetricCardData(label="divider", value=""))

        register_widget_builder("divider_for_test", _build_divider)
        try:
            assert "divider_for_test" in registered_widget_types()
            widget = build_leaf_widget("divider_for_test", "d1", {})
            assert widget.name == "d1"
        finally:
            registry_module._WIDGET_BUILDERS.pop("divider_for_test", None)
