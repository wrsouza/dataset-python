"""Domain entities and value objects for the Message Broker Factory."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class BrokerMessage:
    """Value object representing a message in the broker system."""

    content: str
    destination: str
    broker: str
    published_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, object]:
        return {
            "content": self.content,
            "destination": self.destination,
            "broker": self.broker,
            "published_at": self.published_at.isoformat(),
        }


@dataclass(frozen=True)
class ConsumedMessages:
    """Value object representing a batch of consumed messages."""

    source: str
    broker: str
    messages: list[str]
    count: int

    def to_dict(self) -> dict[str, object]:
        return {
            "source": self.source,
            "broker": self.broker,
            "messages": self.messages,
            "count": self.count,
        }


class BrokerConnectionError(Exception):
    """Raised when a connection to the broker cannot be established."""

    def __init__(self, broker: str, reason: str) -> None:
        self.broker = broker
        self.reason = reason
        super().__init__(f"Cannot connect to {broker}: {reason}")


class QueueNotFoundError(Exception):
    """Raised when a referenced queue/topic does not exist."""

    def __init__(self, name: str, broker: str) -> None:
        self.name = name
        self.broker = broker
        super().__init__(f"Queue '{name}' not found on {broker}")
