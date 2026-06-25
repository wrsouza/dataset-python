"""Domain entities and value objects for the Queue Bridge.

Pure Python dataclasses — no broker-specific types cross this boundary.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class MessagePriority(StrEnum):
    """Priority level for messages handled by PriorityQueueClient."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class BrokerPublishError(Exception):
    """Raised when a broker fails to publish a message.

    Wraps the broker-specific exception so upper layers never depend on
    kombu/celery, pika, or boto3/botocore exception hierarchies.
    """

    def __init__(self, broker: str, reason: str) -> None:
        self.broker = broker
        self.reason = reason
        super().__init__(f"[{broker}] Publish failed: {reason}")


class BrokerConnectionError(Exception):
    """Raised when a broker connection cannot be established."""

    def __init__(self, broker: str, reason: str) -> None:
        self.broker = broker
        self.reason = reason
        super().__init__(f"[{broker}] Connection failed: {reason}")


@dataclass(frozen=True)
class QueueMessage:
    """Value object representing a single message travelling through a queue."""

    queue_name: str
    payload: dict[str, object]
    priority: MessagePriority = MessagePriority.NORMAL
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, object]:
        """Serialise to a plain dict for JSON HTTP responses or wire transport."""
        return {
            "message_id": self.message_id,
            "queue_name": self.queue_name,
            "payload": self.payload,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class BrokerHealth:
    """Value object representing the result of a broker health check."""

    broker: str
    is_healthy: bool
    checked_at: datetime = field(default_factory=datetime.utcnow)
    details: dict[str, str] = field(default_factory=dict)
    error_message: str | None = None

    def to_dict(self) -> dict[str, object]:
        """Serialise to a plain dict for JSON HTTP responses."""
        return {
            "broker": self.broker,
            "is_healthy": self.is_healthy,
            "checked_at": self.checked_at.isoformat(),
            "details": self.details,
            "error_message": self.error_message,
        }


@dataclass(frozen=True)
class EnqueueResult:
    """Value object wrapping the outcome of an enqueue operation."""

    broker: str
    queue_name: str
    message_id: str
    enqueued_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, object]:
        """Serialise to a plain dict for JSON HTTP responses."""
        return {
            "broker": self.broker,
            "queue_name": self.queue_name,
            "message_id": self.message_id,
            "enqueued_at": self.enqueued_at.isoformat(),
        }


@dataclass(frozen=True)
class DequeueResult:
    """Value object wrapping the messages retrieved by a dequeue operation."""

    broker: str
    queue_name: str
    messages: list[dict[str, object]]
    message_count: int
    dequeued_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, object]:
        """Serialise to a plain dict for JSON HTTP responses."""
        return {
            "broker": self.broker,
            "queue_name": self.queue_name,
            "message_count": self.message_count,
            "messages": self.messages,
            "dequeued_at": self.dequeued_at.isoformat(),
        }
