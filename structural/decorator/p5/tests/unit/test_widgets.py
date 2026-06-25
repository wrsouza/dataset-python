"""Unit tests for the ConcreteComponent (TextWidget)."""

from __future__ import annotations

from ui_components.domain.entities import WidgetSpec
from ui_components.infrastructure.widgets import TextWidget


def test_render_includes_widget_id_and_content(widget_spec: WidgetSpec) -> None:
    widget = TextWidget(widget_spec)

    html = widget.render()

    assert widget_spec.widget_id in html
    assert widget_spec.label in html
    assert widget_spec.content in html


def test_describe_returns_label(widget_spec: WidgetSpec) -> None:
    widget = TextWidget(widget_spec)

    assert widget.describe() == widget_spec.label
