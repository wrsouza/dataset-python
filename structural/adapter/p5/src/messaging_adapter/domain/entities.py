"""Domain entities for the Messaging Protocol Adapter.

Message is the broker-agnostic value object shared by every Adapter
(RabbitMQAdapter, KafkaAdapter, ...). Each Adapter translates its native
client's wire format into this single shape — and back — so application
code never has to branch on broker type.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class BrokerType(str, Enum):  # noqa: UP042 — str mixin kept for CLI arg parsing
    """Supported message broker types (used to select an Adapter)."""

    RABBITMQ = "rabbitmq"
    KAFKA = "kafka"


@dataclass(frozen=True)
class Message:
    """Immutable value object shared across every broker Adapter.

    Whatever the native client returns (a pika ``Basic.Deliver`` body, a
    kafka-python ``ConsumerRecord``, ...), the owning Adapter maps it to
    this single structure before handing it to application code.
    """

    topic: str
    value: bytes
    key: str | None = None
    headers: dict[str, str] = field(default_factory=dict)
    timestamp: datetime | None = None

    def decode_value(self, encoding: str = "utf-8") -> str:
        """Decode the raw bytes payload to a string."""
        return self.value.decode(encoding)


@dataclass
class PublishConfig:
    """Parameter object grouping everything a publish operation needs.

    Avoids long positional argument lists (Clean Code) and keeps
    ``MessageBroker.publish`` stable as new options are added (OCP).
    """

    broker: BrokerType
    topic: str
    headers: dict[str, str] = field(default_factory=dict)
    key: str | None = None


@dataclass
class ConsumeConfig:
    """Parameter object grouping everything a consume operation needs."""

    broker: BrokerType
    topic: str
    group_id: str = "default-group"
    limit: int | None = None
    timeout_seconds: float = 5.0


class MessagingError(Exception):
    """Base exception for all messaging domain errors."""


class BrokerConnectionError(MessagingError):
    """Raised when an Adapter fails to connect to its underlying broker."""


class PublishError(MessagingError):
    """Raised when a message cannot be published to the broker."""


class ConsumeError(MessagingError):
    """Raised when messages cannot be consumed from the broker."""
