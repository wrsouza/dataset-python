"""Unit tests for KafkaEventPublisher using a fake producer."""

from __future__ import annotations

import json

from event_sourcing.domain.entities import DomainEvent, EventType
from event_sourcing.infrastructure.kafka_publisher import KafkaEventPublisher


class FakeProducer:
    def __init__(self) -> None:
        self.sent: list[tuple[str, bytes]] = []
        self.flush_count = 0

    def send(self, topic: str, value: bytes) -> None:
        self.sent.append((topic, value))

    def flush(self) -> None:
        self.flush_count += 1


def test_publish_sends_serialised_event_to_default_topic() -> None:
    producer = FakeProducer()
    publisher = KafkaEventPublisher(producer)
    event = DomainEvent.new("acc-1", EventType.FUNDS_DEPOSITED, {"amount": 10.0})

    publisher.publish(event)

    [(topic, body)] = producer.sent
    assert topic == "account-events"
    assert json.loads(body) == {
        "event_id": event.event_id,
        "account_id": "acc-1",
        "event_type": "funds_deposited",
        "payload": {"amount": 10.0},
        "occurred_at": event.occurred_at.isoformat(),
    }
    assert producer.flush_count == 1


def test_publish_uses_custom_topic() -> None:
    producer = FakeProducer()
    publisher = KafkaEventPublisher(producer, topic="custom-topic")
    event = DomainEvent.new("acc-1", EventType.ACCOUNT_OPENED, {})

    publisher.publish(event)

    [(topic, _body)] = producer.sent
    assert topic == "custom-topic"
