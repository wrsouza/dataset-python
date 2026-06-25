"""Concrete Decorator implementations for the UI Component Decorator app.

Each decorator adds exactly one visual/behavioural concern (SRP).
New visual concerns are added by creating new decorators (OCP) —
no existing widget or decorator class needs to change.
"""

from __future__ import annotations

from ui_components.domain.entities import (
    DEFAULT_BADGE_COLOR,
    DEFAULT_BORDER_COLOR,
    InvalidDecorationError,
)
from ui_components.domain.interfaces import UIComponent, UIComponentDecorator

_MAX_BADGE_LENGTH = 12


class BorderDecorator(UIComponentDecorator):
    """Wraps the rendered widget in a colored, rounded border."""

    def __init__(self, wrapped: UIComponent, color: str = DEFAULT_BORDER_COLOR) -> None:
        super().__init__(wrapped)
        self._color = color

    def render(self) -> str:
        inner = self._wrapped.render()
        style = f"border:2px solid {self._color};border-radius:8px;padding:8px;"
        return f'<div style="{style}">{inner}</div>'

    def describe(self) -> str:
        return f"Border({self._wrapped.describe()})"


class TooltipDecorator(UIComponentDecorator):
    """Adds a hover tooltip with explanatory text to the widget."""

    def __init__(self, wrapped: UIComponent, tooltip_text: str) -> None:
        super().__init__(wrapped)
        if not tooltip_text.strip():
            raise InvalidDecorationError("tooltip_text must not be empty")
        self._tooltip_text = tooltip_text

    def render(self) -> str:
        inner = self._wrapped.render()
        return f'<span title="{self._tooltip_text}">{inner}</span>'

    def describe(self) -> str:
        return f"Tooltip({self._wrapped.describe()})"


class BadgeDecorator(UIComponentDecorator):
    """Pins a small status badge (e.g. "NEW", "BETA") onto the widget."""

    def __init__(
        self,
        wrapped: UIComponent,
        text: str,
        color: str = DEFAULT_BADGE_COLOR,
    ) -> None:
        super().__init__(wrapped)
        if len(text) > _MAX_BADGE_LENGTH:
            raise InvalidDecorationError(
                f"badge text exceeds {_MAX_BADGE_LENGTH} characters"
            )
        self._text = text
        self._color = color

    def render(self) -> str:
        inner = self._wrapped.render()
        badge = (
            f'<span style="background:{self._color};color:white;'
            f'border-radius:4px;padding:2px 6px;font-size:0.75em;">'
            f"{self._text}</span>"
        )
        return f'<div style="position:relative;">{badge}{inner}</div>'

    def describe(self) -> str:
        return f"Badge[{self._text}]({self._wrapped.describe()})"


class ShadowDecorator(UIComponentDecorator):
    """Adds a drop shadow, giving the widget a "floating card" look."""

    def render(self) -> str:
        inner = self._wrapped.render()
        style = "box-shadow:0 4px 8px rgba(0,0,0,0.25);"
        return f'<div style="{style}">{inner}</div>'

    def describe(self) -> str:
        return f"Shadow({self._wrapped.describe()})"


class CollapsibleDecorator(UIComponentDecorator):
    """Wraps the widget in a native <details>/<summary> collapsible section."""

    def __init__(self, wrapped: UIComponent, summary: str = "Details") -> None:
        super().__init__(wrapped)
        self._summary = summary

    def render(self) -> str:
        inner = self._wrapped.render()
        return f"<details><summary>{self._summary}</summary>{inner}</details>"

    def describe(self) -> str:
        return f"Collapsible({self._wrapped.describe()})"
