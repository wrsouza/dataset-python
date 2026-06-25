"""ConcreteComponent — the base widget that decorators wrap.

Renders plain HTML for a single widget without any visual extras.
"""

from __future__ import annotations

from ui_components.domain.entities import WidgetSpec
from ui_components.domain.interfaces import UIComponent


class TextWidget(UIComponent):
    """A plain text/card widget — the innermost, undecorated component."""

    def __init__(self, spec: WidgetSpec) -> None:
        self._spec = spec

    def render(self) -> str:
        return (
            f'<div class="ui-widget" id="{self._spec.widget_id}">'
            f"<strong>{self._spec.label}</strong><p>{self._spec.content}</p>"
            f"</div>"
        )

    def describe(self) -> str:
        return self._spec.label
