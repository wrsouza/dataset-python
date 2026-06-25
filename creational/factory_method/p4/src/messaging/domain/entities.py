"""Domain entities for the Message Consumer Factory pattern."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class BrokerType(str, Enum):
    """Supported message broker types."""

    KAFKA = "kafka"
    RABBITMQ = "rabbitmq"
    SQS = "sqs"


@dataclass(frozen=True)
class Message:
    """Immutable value object representing a consumed message.

    Broker-agnostic: every ConcreteProduct maps its native message
    format to this common structure (Factory Method Product contract).
    """

    topic: str
    key: str | None
    value: bytes
    timestamp: datetime
    headers: dict[str, str] = field(default_factory=dict)
    partition: int | None = None
    offset: int | None = None

    def decode_value(self, encoding: str = "utf-8") -> str:
        """Decode the raw bytes value to a string."""
        return self.value.decode(encoding)


@dataclass
class ConsumeConfig:
    """Configuration for a consume session — used as a parameter object.

    Avoids passing more than 3 positional arguments to functions (Clean Code).
    """

    broker: BrokerType
    topic_or_queue: str
    group_id: str = "default-group"
    limit: int | None = None
    timeout_seconds: float = 5.0
    auto_ack: bool = True


class ConsumerError(Exception):
    """Base exception for all consumer domain errors."""


class ConnectionError(ConsumerError):  # noqa: A001 — intentional domain exception name
    """Raised when the consumer fails to connect to the broker."""


class SubscriptionError(ConsumerError):
    """Raised when the consumer cannot subscribe to a topic or queue."""


class AckError(ConsumerError):
    """Raised when acknowledging a message fails."""
