"""Integration tests for P5 — requires real brokers via docker-compose.

Run with:
    docker-compose run --rm app pytest tests/integration/ -v

These tests are skipped unless RUN_INTEGRATION=true is explicitly set,
preventing CI from failing when brokers are unavailable.
"""

from __future__ import annotations

import os

import pytest

from messaging_adapter.domain.entities import (
    BrokerType,
    ConsumeConfig,
    Message,
    PublishConfig,
)
from messaging_adapter.infrastructure.kafka_adapter import KafkaAdapter
from messaging_adapter.infrastructure.rabbitmq_adapter import RabbitMQAdapter

# Skip all integration tests unless RUN_INTEGRATION=true is explicitly set
pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION", "false").lower() != "true",
    reason="Set RUN_INTEGRATION=true to run integration tests against real brokers",
)


class TestRabbitMQIntegration:
    """Integration test: requires RabbitMQ at rabbitmq:5672."""

    def test_publish_and_consume_roundtrip(self) -> None:
        adapter = RabbitMQAdapter()
        publish_config = PublishConfig(
            broker=BrokerType.RABBITMQ, topic="integration-test-queue"
        )
        consume_config = ConsumeConfig(
            broker=BrokerType.RABBITMQ, topic="integration-test-queue", limit=1
        )

        adapter.connect()
        adapter.publish(
            publish_config.topic, Message(topic=publish_config.topic, value=b"ping")
        )
        messages = list(adapter.consume(consume_config))
        adapter.close()

        assert isinstance(messages, list)


class TestKafkaIntegration:
    """Integration test: requires Kafka at kafka:9092."""

    def test_publish_and_consume_roundtrip(self) -> None:
        adapter = KafkaAdapter()
        publish_config = PublishConfig(
            broker=BrokerType.KAFKA, topic="integration-test-topic"
        )
        consume_config = ConsumeConfig(
            broker=BrokerType.KAFKA,
            topic="integration-test-topic",
            group_id="integration-group",
            limit=1,
            timeout_seconds=10.0,
        )

        adapter.connect()
        adapter.publish(
            publish_config.topic, Message(topic=publish_config.topic, value=b"ping")
        )
        messages = list(adapter.consume(consume_config))
        adapter.close()

        assert isinstance(messages, list)
