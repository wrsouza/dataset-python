"""Core entities for the event bus mediator domain."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class Event:
    """A single named event, with an arbitrary JSON-serialisable payload."""

    event_type: str
    payload: dict[str, object]
    published_at: datetime = field(default_factory=lambda: datetime.now(UTC))
