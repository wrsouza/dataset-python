"""Unit tests for the concrete Decorator implementations."""

from __future__ import annotations

import pytest

from ui_components.domain.entities import InvalidDecorationError, WidgetSpec
from ui_components.infrastructure.decorators import (
    BadgeDecorator,
    BorderDecorator,
    CollapsibleDecorator,
    ShadowDecorator,
    TooltipDecorator,
)
from ui_components.infrastructure.widgets import TextWidget


def test_border_decorator_wraps_render_in_border_div(widget_spec: WidgetSpec) -> None:
    widget = BorderDecorator(TextWidget(widget_spec), color="#000000")

    html = widget.render()

    assert "border:2px solid #000000" in html
    assert widget_spec.content in html


def test_border_decorator_describe_wraps_inner_label(widget_spec: WidgetSpec) -> None:
    widget = BorderDecorator(TextWidget(widget_spec))

    assert widget.describe() == f"Border({widget_spec.label})"


def test_tooltip_decorator_adds_title_attribute(widget_spec: WidgetSpec) -> None:
    widget = TooltipDecorator(TextWidget(widget_spec), "explains the metric")

    html = widget.render()

    assert 'title="explains the metric"' in html


def test_tooltip_decorator_rejects_empty_text(widget_spec: WidgetSpec) -> None:
    with pytest.raises(InvalidDecorationError):
        TooltipDecorator(TextWidget(widget_spec), "   ")


def test_badge_decorator_renders_badge_text(widget_spec: WidgetSpec) -> None:
    widget = BadgeDecorator(TextWidget(widget_spec), "NEW")

    html = widget.render()

    assert ">NEW<" in html


def test_badge_decorator_rejects_overly_long_text(widget_spec: WidgetSpec) -> None:
    with pytest.raises(InvalidDecorationError):
        BadgeDecorator(TextWidget(widget_spec), "THIS BADGE IS WAY TOO LONG")


def test_shadow_decorator_adds_box_shadow_style(widget_spec: WidgetSpec) -> None:
    widget = ShadowDecorator(TextWidget(widget_spec))

    assert "box-shadow" in widget.render()


def test_collapsible_decorator_wraps_in_details_summary(
    widget_spec: WidgetSpec,
) -> None:
    widget = CollapsibleDecorator(TextWidget(widget_spec), summary="More info")

    html = widget.render()

    assert "<details>" in html
    assert "<summary>More info</summary>" in html


def test_decorators_stack_and_compose_describe(widget_spec: WidgetSpec) -> None:
    widget = BadgeDecorator(
        ShadowDecorator(BorderDecorator(TextWidget(widget_spec))), "HOT"
    )

    description = widget.describe()

    assert description == f"Badge[HOT](Shadow(Border({widget_spec.label})))"


def test_decorators_stack_and_compose_render(widget_spec: WidgetSpec) -> None:
    widget = BadgeDecorator(
        ShadowDecorator(BorderDecorator(TextWidget(widget_spec))), "HOT"
    )

    html = widget.render()

    assert "box-shadow" in html
    assert "border:2px solid" in html
    assert ">HOT<" in html
    assert widget_spec.content in html
