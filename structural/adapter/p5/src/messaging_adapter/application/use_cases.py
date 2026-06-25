"""Application use cases — depend only on the MessageBroker Target.

DIP: none of these classes import pika, kafka-python, or any concrete
Adapter. They receive a ``MessageBroker`` via constructor injection,
so they work identically whether it's backed by RabbitMQ, Kafka, or a
test double (LSP).
"""

from __future__ import annotations

from messaging_adapter.domain.entities import (
    BrokerType,
    ConsumeConfig,
    Message,
    PublishConfig,
)
from messaging_adapter.domain.interfaces import MessageBroker


class PublishMessageUseCase:
    """Publish a single message through any MessageBroker.

    SRP: this class only orchestrates the connect → publish → close
    lifecycle for a publish operation.
    """

    def __init__(self, broker: MessageBroker) -> None:
        self._broker = broker

    def execute(self, config: PublishConfig, payload: bytes) -> Message:
        """Connect, publish *payload* to *config.topic*, then close.

        Args:
            config: publish session parameters.
            payload: raw bytes to send.

        Returns:
            The Message that was published.
        """
        message = Message(
            topic=config.topic,
            value=payload,
            key=config.key,
            headers=config.headers,
        )
        self._broker.connect()
        try:
            self._broker.publish(config.topic, message)
        finally:
            self._broker.close()
        return message


class ConsumeMessagesUseCase:
    """Consume a bounded batch of messages through any MessageBroker.

    SRP: this class only orchestrates the connect → consume → close
    lifecycle and collects results into a list.
    """

    def __init__(self, broker: MessageBroker) -> None:
        self._broker = broker

    def execute(self, config: ConsumeConfig) -> list[Message]:
        """Connect, consume up to *config.limit* messages, then close.

        Args:
            config: consume session parameters.

        Returns:
            List of consumed messages, at most config.limit items.
        """
        self._broker.connect()
        try:
            return list(self._broker.consume(config))
        finally:
            self._broker.close()


class ListBrokersUseCase:
    """Return display metadata for every registered broker Adapter."""

    def __init__(self, display_names: dict[BrokerType, str]) -> None:
        self._display_names = display_names

    def execute(self) -> list[dict[str, str]]:
        """Return broker slugs and human-readable names for CLI display."""
        return [
            {"slug": slug.value, "name": name}
            for slug, name in self._display_names.items()
        ]
