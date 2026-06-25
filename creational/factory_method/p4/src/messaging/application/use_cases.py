"""Application use cases for the Message Consumer Factory.

Use cases depend on abstractions (ConsumerFactory, MessageConsumer),
never on concrete Kafka / RabbitMQ / SQS classes (DIP).
Each use case has a single responsibility (SRP).
"""
from __future__ import annotations

from collections.abc import Iterator

from messaging.domain.entities import ConsumeConfig, Message
from messaging.domain.interfaces import ConsumerFactory, MessageConsumer


class ConsumeMessagesUseCase:
    """Orchestrate a consume session using any ConsumerFactory.

    SRP: this class only knows how to orchestrate the consume loop.
    DIP: receives ConsumerFactory via constructor — testable with any fake.
    """

    def __init__(self, factory: ConsumerFactory) -> None:
        self._factory = factory

    def execute(self, config: ConsumeConfig) -> list[Message]:
        """Run a full consume session and return collected messages.

        Args:
            config: session parameters (broker type, topic, limit, …).

        Returns:
            List of consumed messages, at most config.limit items.
        """
        return self._factory.consume_all(config)


class StreamMessagesUseCase:
    """Stream messages one-by-one — suitable for long-running CLI pipelines.

    Yields messages lazily instead of loading all into memory (contrast with
    ConsumeMessagesUseCase). Caller is responsible for ack and close.
    """

    def __init__(self, factory: ConsumerFactory) -> None:
        self._factory = factory

    def execute(self, config: ConsumeConfig) -> Iterator[tuple[Message, MessageConsumer]]:
        """Yield (message, consumer) pairs so the caller can ack.

        Args:
            config: session parameters.

        Yields:
            Tuple of (Message, MessageConsumer) — caller should call
            consumer.ack(message) after processing each message.
        """
        consumer = self._factory.create_consumer(config)
        consumer.connect()
        consumer.subscribe(config.topic_or_queue)
        count = 0
        try:
            for message in consumer.consume():
                yield message, consumer
                count += 1
                if config.limit is not None and count >= config.limit:
                    break
        finally:
            consumer.close()


class ListBrokersUseCase:
    """Return metadata about all registered broker factories."""

    def __init__(self, registry: dict[str, ConsumerFactory]) -> None:
        self._registry = registry

    def execute(self) -> list[dict[str, str]]:
        """Return broker names and slugs for display in CLI help."""
        return [
            {"slug": slug, "name": factory.get_broker_name()}
            for slug, factory in self._registry.items()
        ]
