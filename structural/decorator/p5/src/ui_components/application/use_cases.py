"""Application layer — composes decorated widgets for the dashboard.

Each `build_*_widget` function is the composition root for one dashboard
card: it wires a base `TextWidget` through a chosen stack of decorators.
Decorator order matters (outer wraps inner) but no existing decorator or
widget class is ever modified to support a new combination (OCP).
"""

from __future__ import annotations

from ui_components.domain.entities import WidgetSpec
from ui_components.domain.interfaces import UIComponent
from ui_components.infrastructure.decorators import (
    BadgeDecorator,
    BorderDecorator,
    CollapsibleDecorator,
    ShadowDecorator,
    TooltipDecorator,
)
from ui_components.infrastructure.widgets import TextWidget


def build_plain_widget(spec: WidgetSpec) -> UIComponent:
    """Return the undecorated base widget — useful as a baseline comparison."""
    return TextWidget(spec)


def build_highlighted_widget(spec: WidgetSpec, tooltip_text: str) -> UIComponent:
    """Border + Tooltip — emphasizes a widget and explains it on hover."""
    widget: UIComponent = TextWidget(spec)
    widget = BorderDecorator(widget)
    widget = TooltipDecorator(widget, tooltip_text)
    return widget


def build_announcement_widget(spec: WidgetSpec, badge_text: str = "NEW") -> UIComponent:
    """Badge + Shadow + Border — a card meant to stand out on the dashboard."""
    widget: UIComponent = TextWidget(spec)
    widget = BorderDecorator(widget)
    widget = ShadowDecorator(widget)
    widget = BadgeDecorator(widget, badge_text)
    return widget


def build_advanced_panel_widget(spec: WidgetSpec, summary: str) -> UIComponent:
    """Collapsible + Border — hides verbose content behind a summary toggle."""
    widget: UIComponent = TextWidget(spec)
    widget = BorderDecorator(widget)
    widget = CollapsibleDecorator(widget, summary)
    return widget


def build_full_stack_widget(
    spec: WidgetSpec, tooltip_text: str, badge_text: str
) -> UIComponent:
    """Stacks every decorator to show that layers compose without conflict."""
    widget: UIComponent = TextWidget(spec)
    widget = BorderDecorator(widget)
    widget = ShadowDecorator(widget)
    widget = TooltipDecorator(widget, tooltip_text)
    widget = BadgeDecorator(widget, badge_text)
    return widget
