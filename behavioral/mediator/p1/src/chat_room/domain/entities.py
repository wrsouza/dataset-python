"""Core entities for the chat room mediator domain."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class ChatMessage:
    """A single message exchanged in a chat room."""

    room_id: str
    sender_id: str
    text: str
    sent_at: datetime = field(default_factory=lambda: datetime.now(UTC))
