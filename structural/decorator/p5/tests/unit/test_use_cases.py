"""Unit tests for the application-layer widget composition functions."""

from __future__ import annotations

from ui_components.application.use_cases import (
    build_advanced_panel_widget,
    build_announcement_widget,
    build_full_stack_widget,
    build_highlighted_widget,
    build_plain_widget,
)
from ui_components.domain.entities import WidgetSpec


def test_build_plain_widget_has_no_decoration(widget_spec: WidgetSpec) -> None:
    widget = build_plain_widget(widget_spec)

    assert widget.describe() == widget_spec.label


def test_build_highlighted_widget_applies_border_and_tooltip(
    widget_spec: WidgetSpec,
) -> None:
    widget = build_highlighted_widget(widget_spec, "hover hint")

    html = widget.render()
    assert "border:2px solid" in html
    assert 'title="hover hint"' in html
    assert widget.describe() == f"Tooltip(Border({widget_spec.label}))"


def test_build_announcement_widget_applies_badge_shadow_border(
    widget_spec: WidgetSpec,
) -> None:
    widget = build_announcement_widget(widget_spec, badge_text="HOT")

    html = widget.render()
    assert "box-shadow" in html
    assert "border:2px solid" in html
    assert ">HOT<" in html
    assert widget.describe() == f"Badge[HOT](Shadow(Border({widget_spec.label})))"


def test_build_advanced_panel_widget_is_collapsible(widget_spec: WidgetSpec) -> None:
    widget = build_advanced_panel_widget(widget_spec, summary="Open me")

    html = widget.render()
    assert "<summary>Open me</summary>" in html
    assert widget.describe() == f"Collapsible(Border({widget_spec.label}))"


def test_build_full_stack_widget_applies_all_layers(widget_spec: WidgetSpec) -> None:
    widget = build_full_stack_widget(widget_spec, "tip", "NEW")

    html = widget.render()
    assert "border:2px solid" in html
    assert "box-shadow" in html
    assert 'title="tip"' in html
    assert ">NEW<" in html
