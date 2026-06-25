"""Abstract interfaces for the Message Broker Factory pattern.

Defines AbstractFactory (MessageBrokerFactory) and three AbstractProducts:
Producer, Consumer, QueueAdmin.

ISP: each product protocol is minimal and focused.
Clients that only publish never depend on Consumer or QueueAdmin.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol

# ── AbstractProducts (ISP: separate protocols per role) ────────────────────────


class Producer(Protocol):
    """AbstractProduct: publishes messages to a queue or topic."""

    def publish(self, destination: str, message: str) -> None:
        """Publish a message to the given queue/topic name."""
        ...

    def close(self) -> None:
        """Release any resources held by the producer."""
        ...


class Consumer(Protocol):
    """AbstractProduct: consumes messages from a queue or topic."""

    def consume(self, source: str, max_messages: int) -> list[str]:
        """Pull up to max_messages messages from the given source."""
        ...

    def acknowledge(self, message_id: str) -> None:
        """Acknowledge that a message has been processed."""
        ...

    def close(self) -> None:
        """Release any resources held by the consumer."""
        ...


class QueueAdmin(Protocol):
    """AbstractProduct: manages queue/topic lifecycle."""

    def create_queue(self, name: str) -> str:
        """Create a queue/topic and return its identifier."""
        ...

    def delete_queue(self, name: str) -> None:
        """Delete a queue/topic by name."""
        ...

    def list_queues(self) -> list[str]:
        """Return names of all existing queues/topics."""
        ...


# ── AbstractFactory ────────────────────────────────────────────────────────────


class MessageBrokerFactory(ABC):
    """AbstractFactory: creates Producer, Consumer, QueueAdmin for a broker.

    OCP: new brokers (e.g. Pulsar, NATS) are added via new subclasses.
    ISP: each product protocol is independent — callers choose what they need.
    """

    @abstractmethod
    def create_producer(self) -> Producer:
        """Create a broker-specific message producer."""
        ...

    @abstractmethod
    def create_consumer(self) -> Consumer:
        """Create a broker-specific message consumer."""
        ...

    @abstractmethod
    def create_admin(self) -> QueueAdmin:
        """Create a broker-specific queue/topic administrator."""
        ...

    @abstractmethod
    def get_broker_name(self) -> str:
        """Return the human-readable broker name (e.g. 'rabbitmq')."""
        ...
