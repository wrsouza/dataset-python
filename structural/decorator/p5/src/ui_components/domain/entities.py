"""Value objects and domain errors for the UI Component Decorator app."""

from __future__ import annotations

from dataclasses import dataclass, field

DEFAULT_BORDER_COLOR = "#4B8BBE"
DEFAULT_BADGE_COLOR = "#E63946"


@dataclass(frozen=True)
class WidgetSpec:
    """Describes the base widget before any decoration is applied."""

    widget_id: str
    label: str
    content: str
    tags: tuple[str, ...] = field(default_factory=tuple)


class InvalidDecorationError(Exception):
    """Raised when a decorator receives configuration it cannot apply."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Invalid decoration: {reason}")
