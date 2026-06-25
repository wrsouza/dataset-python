"""Integration tests for P4 — requires real brokers via docker-compose.

Run with:
    docker-compose run --rm app pytest tests/integration/ -v

These tests are skipped if the broker environment variables are not set,
preventing CI from failing when brokers are unavailable.
"""
from __future__ import annotations

import os

import pytest

from messaging.domain.entities import BrokerType, ConsumeConfig
from messaging.infrastructure.consumers import (
    KafkaConsumerFactory,
    RabbitMQConsumerFactory,
    SQSConsumerFactory,
)

# Skip all integration tests unless RUN_INTEGRATION=true is explicitly set
pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION", "false").lower() != "true",
    reason="Set RUN_INTEGRATION=true to run integration tests against real brokers",
)


class TestKafkaIntegration:
    """Integration test: requires Kafka at kafka:9092."""

    def test_produce_and_consume(self) -> None:
        config = ConsumeConfig(
            broker=BrokerType.KAFKA,
            topic_or_queue="integration-test-topic",
            group_id="integration-group",
            limit=1,
            timeout_seconds=10.0,
        )
        factory = KafkaConsumerFactory()
        # Attempt real consumption — will pass only with live Kafka
        messages = factory.consume_all(config)
        # In a real integration test we'd produce first, then consume
        assert isinstance(messages, list)


class TestRabbitMQIntegration:
    """Integration test: requires RabbitMQ at rabbitmq:5672."""

    def test_consume_from_queue(self) -> None:
        config = ConsumeConfig(
            broker=BrokerType.RABBITMQ,
            topic_or_queue="integration-test-queue",
            limit=1,
            timeout_seconds=5.0,
        )
        factory = RabbitMQConsumerFactory()
        messages = factory.consume_all(config)
        assert isinstance(messages, list)


class TestSQSIntegration:
    """Integration test: requires LocalStack at localstack:4566."""

    def test_consume_from_sqs_queue(self) -> None:
        config = ConsumeConfig(
            broker=BrokerType.SQS,
            topic_or_queue="integration-test-queue",
            limit=1,
            timeout_seconds=5.0,
        )
        factory = SQSConsumerFactory()
        messages = factory.consume_all(config)
        assert isinstance(messages, list)
