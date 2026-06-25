"""Integration tests exercising the full decoration chain end-to-end.

These tests mimic what the Streamlit app does in `_build_widget_from_selection`
but operate directly on the application/use case layer, validating the whole
domain -> application -> infrastructure flow without mocking anything.
"""

from __future__ import annotations

from ui_components.application.use_cases import build_full_stack_widget
from ui_components.domain.entities import WidgetSpec
from ui_components.infrastructure.decorators import (
    BadgeDecorator,
    BorderDecorator,
    CollapsibleDecorator,
    ShadowDecorator,
    TooltipDecorator,
)
from ui_components.infrastructure.widgets import TextWidget


def test_full_dashboard_card_renders_consistent_html() -> None:
    spec = WidgetSpec(
        widget_id="dashboard-card-1",
        label="Active Users",
        content="1,204 users online now",
    )

    widget = build_full_stack_widget(
        spec, tooltip_text="Live metric", badge_text="LIVE"
    )
    html = widget.render()

    assert spec.widget_id in html
    assert spec.content in html
    assert ">LIVE<" in html
    assert 'title="Live metric"' in html


def test_arbitrary_decorator_order_is_supported() -> None:
    """The Decorator pattern allows any order; verify two orders both work."""
    spec = WidgetSpec(widget_id="card-2", label="Errors", content="0 errors today")

    order_a = CollapsibleDecorator(
        BadgeDecorator(BorderDecorator(TextWidget(spec)), "OK"), summary="Status"
    )
    order_b = BorderDecorator(
        BadgeDecorator(CollapsibleDecorator(TextWidget(spec), summary="Status"), "OK")
    )

    assert "<details>" in order_a.render()
    assert "<details>" in order_b.render()
    assert order_a.describe() != order_b.describe()


def test_shadow_and_tooltip_compose_without_interference() -> None:
    spec = WidgetSpec(widget_id="card-3", label="Latency", content="42ms p99")

    widget = TooltipDecorator(ShadowDecorator(TextWidget(spec)), "p99 latency")
    html = widget.render()

    assert "box-shadow" in html
    assert 'title="p99 latency"' in html
    assert spec.content in html
