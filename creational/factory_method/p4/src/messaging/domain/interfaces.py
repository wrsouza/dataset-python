"""Domain interfaces for the Message Consumer Factory pattern.

Defines the Creator ABC and Product Protocol following Factory Method.
ISP: MessageConsumer has the minimum viable interface — connect, subscribe,
consume, ack, close. Each client uses only what it needs.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Protocol, runtime_checkable

from messaging.domain.entities import ConsumeConfig, Message


@runtime_checkable
class MessageConsumer(Protocol):
    """Product interface — every concrete consumer must satisfy this contract.

    ISP: only 5 focused methods. Clients that only read never need to touch ack.
    """

    def connect(self) -> None:
        """Open a connection to the broker.

        Raises:
            ConnectionError: if the broker is unreachable.
        """
        ...

    def subscribe(self, topic_or_queue: str) -> None:
        """Subscribe to a topic (Kafka), queue (RabbitMQ/SQS).

        Args:
            topic_or_queue: name of the topic or queue to consume from.

        Raises:
            SubscriptionError: if the subscription cannot be established.
        """
        ...

    def consume(self) -> Iterator[Message]:
        """Yield messages one by one.

        The iterator stops when the limit is reached or the connection closes.

        Yields:
            Message: broker-agnostic message value object.
        """
        ...

    def ack(self, message: Message) -> None:
        """Acknowledge a successfully processed message.

        Args:
            message: the message to acknowledge.

        Raises:
            AckError: if the acknowledgement fails.
        """
        ...

    def close(self) -> None:
        """Close the connection and release resources."""
        ...


class ConsumerFactory(ABC):
    """Creator — declares the factory method that subclasses override.

    The Creator orchestrates consumption via _any_ MessageConsumer without
    knowing which concrete broker will be used (DIP).

    Adding a new broker = new ConcreteCreator in infrastructure/, zero
    changes here (OCP).
    """

    @abstractmethod
    def create_consumer(self, config: ConsumeConfig) -> MessageConsumer:
        """Factory method: return a MessageConsumer for this broker.

        Args:
            config: connection and subscription parameters.

        Returns:
            A fully configured (but not yet connected) MessageConsumer.
        """
        ...

    def get_broker_name(self) -> str:
        """Return a human-readable broker name for display purposes."""
        return self.__class__.__name__.replace("ConsumerFactory", "")

    def consume_all(self, config: ConsumeConfig) -> list[Message]:
        """Template method: connect → subscribe → consume → close.

        Concrete consumers don't need to implement this orchestration;
        only the factory method is overridden (Factory Method pattern).

        Args:
            config: session configuration.

        Returns:
            List of consumed messages up to config.limit.
        """
        consumer = self.create_consumer(config)
        consumer.connect()
        consumer.subscribe(config.topic_or_queue)

        messages: list[Message] = []
        for message in consumer.consume():
            messages.append(message)
            if config.auto_ack:
                consumer.ack(message)
            if config.limit is not None and len(messages) >= config.limit:
                break

        consumer.close()
        return messages
