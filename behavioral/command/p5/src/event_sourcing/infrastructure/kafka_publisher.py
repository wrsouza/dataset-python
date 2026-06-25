"""Kafka-backed implementation of EventPublisher."""

from __future__ import annotations

import json
from typing import Protocol

from event_sourcing.domain.entities import DomainEvent
from event_sourcing.domain.interfaces import EventPublisher


class KafkaProducerLike(Protocol):
    """Minimal kafka-python KafkaProducer contract this publisher relies on."""

    def send(self, topic: str, value: bytes) -> object: ...

    def flush(self) -> None: ...


class KafkaEventPublisher(EventPublisher):
    """Publishes each domain event to a Kafka topic for downstream consumers."""

    def __init__(
        self, producer: KafkaProducerLike, topic: str = "account-events"
    ) -> None:
        self._producer = producer
        self._topic = topic

    def publish(self, event: DomainEvent) -> None:
        body = json.dumps(
            {
                "event_id": event.event_id,
                "account_id": event.account_id,
                "event_type": event.event_type.value,
                "payload": event.payload,
                "occurred_at": event.occurred_at.isoformat(),
            }
        ).encode("utf-8")
        self._producer.send(self._topic, value=body)
        self._producer.flush()
