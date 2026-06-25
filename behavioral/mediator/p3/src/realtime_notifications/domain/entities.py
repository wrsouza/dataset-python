"""Core entities for the real-time notifications mediator domain."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class Notification:
    """A single notification broadcast to every client subscribed to a group."""

    group: str
    message: dict[str, object]
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
