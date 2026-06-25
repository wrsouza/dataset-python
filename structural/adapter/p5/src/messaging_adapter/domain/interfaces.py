"""Target interface — MessageBroker Protocol.

This is the Adapter pattern's *Target*: the unified interface that client
code (CLI commands, use cases) is written against. Two very different
native client libraries — pika (RabbitMQ) and kafka-python (Kafka) — are
the *Adaptees*; their incompatible APIs are reconciled by concrete
Adapters (``RabbitMQAdapter``, ``KafkaAdapter``) that implement this
Protocol (see ``infrastructure/rabbitmq_adapter.py`` and
``infrastructure/kafka_adapter.py``).

ISP: only 4 lifecycle/IO methods — the minimum viable contract for a
broker client. DIP: application code and the CLI depend exclusively on
this Protocol, never importing pika or kafka directly.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Protocol, runtime_checkable

from messaging_adapter.domain.entities import ConsumeConfig, Message


@runtime_checkable
class MessageBroker(Protocol):
    """Target: unified publish/consume interface for any message broker.

    Every Adapter (RabbitMQAdapter, KafkaAdapter, ...) must satisfy this
    contract identically (LSP) so that application code can swap brokers
    without any change in behaviour expectations.
    """

    def connect(self) -> None:
        """Open a connection to the underlying broker.

        Raises:
            BrokerConnectionError: if the broker is unreachable.
        """
        ...

    def publish(self, topic: str, message: Message) -> None:
        """Publish *message* to *topic* (or queue, depending on broker).

        Args:
            topic: destination topic/queue name.
            message: broker-agnostic message to send.

        Raises:
            PublishError: if the message cannot be delivered.
        """
        ...

    def consume(self, config: ConsumeConfig) -> Iterator[Message]:
        """Yield messages from *config.topic* up to *config.limit*.

        Args:
            config: consume session parameters.

        Yields:
            Message: broker-agnostic message value object.

        Raises:
            ConsumeError: if messages cannot be retrieved.
        """
        ...

    def close(self) -> None:
        """Close the connection and release any held resources."""
        ...
