"""Unit tests for KafkaEtlEventPublisher."""

from __future__ import annotations

import json

from etl_pipeline_template.infrastructure.kafka_publisher import (
    KafkaEtlEventPublisher,
)


class FakeProducer:
    def __init__(self) -> None:
        self.sent: list[tuple[str, bytes]] = []
        self.flushed = False

    def send(self, topic: str, value: bytes) -> object:
        self.sent.append((topic, value))
        return object()

    def flush(self) -> None:
        self.flushed = True


def test_publish_completion_sends_and_flushes() -> None:
    producer = FakeProducer()
    publisher = KafkaEtlEventPublisher(producer, topic="etl-events")

    publisher.publish_completion("customer_etl", 5)

    assert producer.flushed is True
    topic, body = producer.sent[0]
    assert topic == "etl-events"
    assert json.loads(body) == {"pipeline_name": "customer_etl", "records_loaded": 5}
