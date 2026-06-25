"""Application use cases for the Message Broker Factory.

Client role: each use case receives a MessageBrokerFactory and delegates
to the appropriate product. No broker-specific imports appear here.
"""

from __future__ import annotations

from broker_factory.domain.entities import BrokerMessage, ConsumedMessages
from broker_factory.domain.interfaces import MessageBrokerFactory


class PublishMessageUseCase:
    """Publish a single message to a queue/topic via the injected broker factory.

    ISP + DIP: only uses Producer — does not depend on Consumer or QueueAdmin.
    """

    def __init__(self, factory: MessageBrokerFactory) -> None:
        self._factory = factory

    def execute(self, destination: str, message: str) -> BrokerMessage:
        """Publish the message and return a BrokerMessage value object."""
        producer = self._factory.create_producer()
        try:
            producer.publish(destination, message)
        finally:
            producer.close()
        return BrokerMessage(
            content=message,
            destination=destination,
            broker=self._factory.get_broker_name(),
        )


class ConsumeMessagesUseCase:
    """Consume messages from a queue/topic via the injected broker factory.

    ISP: only uses Consumer — does not depend on Producer or QueueAdmin.
    """

    def __init__(self, factory: MessageBrokerFactory) -> None:
        self._factory = factory

    def execute(self, source: str, max_messages: int = 10) -> ConsumedMessages:
        """Pull messages from the source and return a ConsumedMessages value object."""
        consumer = self._factory.create_consumer()
        try:
            messages = consumer.consume(source, max_messages)
        finally:
            consumer.close()
        return ConsumedMessages(
            source=source,
            broker=self._factory.get_broker_name(),
            messages=messages,
            count=len(messages),
        )


class CreateQueueUseCase:
    """Create a queue/topic via the injected broker factory.

    ISP: only uses QueueAdmin.
    """

    def __init__(self, factory: MessageBrokerFactory) -> None:
        self._factory = factory

    def execute(self, name: str) -> dict[str, str]:
        """Create the queue and return its identifier."""
        admin = self._factory.create_admin()
        queue_id = admin.create_queue(name)
        return {
            "name": name,
            "identifier": queue_id,
            "broker": self._factory.get_broker_name(),
        }


class ListQueuesUseCase:
    """List all queues/topics for the configured broker."""

    def __init__(self, factory: MessageBrokerFactory) -> None:
        self._factory = factory

    def execute(self) -> dict[str, object]:
        """Return all queue/topic names for this broker."""
        admin = self._factory.create_admin()
        queues = admin.list_queues()
        return {
            "broker": self._factory.get_broker_name(),
            "queues": queues,
            "count": len(queues),
        }
