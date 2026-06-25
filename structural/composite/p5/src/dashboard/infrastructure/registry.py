"""Registry of widget-type builders, enabling OCP-friendly extension.

New leaf widget types can be added by writing a builder function and
calling `register_widget_builder` — `build_component_tree` in
`definition_parser.py` and all container classes stay untouched. This
keeps the system Open for extension (new widgets) but Closed for
modification (no existing code is edited to add a type).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from src.dashboard.domain.entities import ChartData, MetricCardData, TextBlockData
from src.dashboard.domain.exceptions import UnknownComponentTypeError
from src.dashboard.domain.interfaces import DashboardComponent
from src.dashboard.infrastructure.widgets import ChartWidget, MetricCard, TextBlock

WidgetBuilder = Callable[[str, dict[str, Any]], DashboardComponent]

_WIDGET_BUILDERS: dict[str, WidgetBuilder] = {}


def register_widget_builder(component_type: str, builder: WidgetBuilder) -> None:
    """Register a factory function for a leaf widget type identifier."""
    _WIDGET_BUILDERS[component_type] = builder


def build_leaf_widget(
    component_type: str, name: str, props: dict[str, Any]
) -> DashboardComponent:
    """Build a leaf widget instance for `component_type`, or raise.

    Raises:
        UnknownComponentTypeError: when no builder is registered.
    """
    builder = _WIDGET_BUILDERS.get(component_type)
    if builder is None:
        raise UnknownComponentTypeError(component_type)
    return builder(name, props)


def registered_widget_types() -> list[str]:
    """Return all currently registered leaf widget type identifiers."""
    return sorted(_WIDGET_BUILDERS)


def _build_metric_card(name: str, props: dict[str, Any]) -> DashboardComponent:
    data = MetricCardData(
        label=props.get("label", name),
        value=str(props.get("value", "")),
        delta=props.get("delta"),
    )
    return MetricCard(name, data)


def _build_text_block(name: str, props: dict[str, Any]) -> DashboardComponent:
    data = TextBlockData(
        content=props.get("content", ""),
        markdown=bool(props.get("markdown", True)),
    )
    return TextBlock(name, data)


def _build_chart(name: str, props: dict[str, Any]) -> DashboardComponent:
    data = ChartData(
        chart_type=props.get("chart_type", "line"),
        series=dict(props.get("series", {})),
        x_labels=list(props.get("x_labels", [])),
    )
    return ChartWidget(name, data)


register_widget_builder("metric_card", _build_metric_card)
register_widget_builder("text_block", _build_text_block)
register_widget_builder("chart", _build_chart)
