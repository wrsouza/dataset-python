"""Core entities for the service bus mediator domain."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class ServiceMessage:
    """A single message exchanged between services through the bus."""

    sender_service: str
    payload: dict[str, object]
    sent_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    receipt_handle: str | None = None
