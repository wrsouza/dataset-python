"""Integration tests exercising real broker product families.

These tests require the docker-compose services (rabbitmq, kafka, localstack)
to be running:

    docker-compose up -d rabbitmq kafka localstack
    pytest tests/integration -m integration

Each test is skipped automatically if its broker is unreachable, so the suite
stays green in environments without the docker-compose stack (e.g. plain
`pytest` during local unit-test runs).
"""

from __future__ import annotations

import os
import socket
from collections.abc import Iterator

import pytest

from broker_factory.infrastructure.factories import (
    KafkaFactory,
    RabbitMQFactory,
    SQSFactory,
)

pytestmark = pytest.mark.integration


def _port_is_open(host: str, port: int, timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


@pytest.fixture
def rabbitmq_factory() -> Iterator[RabbitMQFactory]:
    url = os.environ.get("RABBITMQ_URL", "amqp://app:secret@localhost:5672/")
    if not _port_is_open("localhost", 5672):
        pytest.skip("RabbitMQ service is not reachable on localhost:5672")
    return RabbitMQFactory(connection_url=url)


@pytest.fixture
def kafka_factory() -> Iterator[KafkaFactory]:
    servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    if not _port_is_open("localhost", 9092):
        pytest.skip("Kafka service is not reachable on localhost:9092")
    return KafkaFactory(bootstrap_servers=servers)


@pytest.fixture
def sqs_factory() -> Iterator[SQSFactory]:
    endpoint = os.environ.get("LOCALSTACK_URL", "http://localhost:4566")
    if not _port_is_open("localhost", 4566):
        pytest.skip("LocalStack service is not reachable on localhost:4566")
    return SQSFactory(endpoint_url=endpoint)


class TestRabbitMQIntegration:
    def test_publish_and_consume_round_trip(
        self, rabbitmq_factory: RabbitMQFactory
    ) -> None:
        admin = rabbitmq_factory.create_admin()
        admin.create_queue("integration-test-queue")

        producer = rabbitmq_factory.create_producer()
        producer.publish("integration-test-queue", "integration-message")
        producer.close()

        consumer = rabbitmq_factory.create_consumer()
        messages = consumer.consume("integration-test-queue", max_messages=1)
        consumer.close()

        assert messages == ["integration-message"]

        admin.delete_queue("integration-test-queue")


class TestKafkaIntegration:
    def test_create_topic_and_publish(self, kafka_factory: KafkaFactory) -> None:
        admin = kafka_factory.create_admin()
        admin.create_queue("integration-test-topic")

        producer = kafka_factory.create_producer()
        producer.publish("integration-test-topic", "integration-message")
        producer.close()

        topics = admin.list_queues()

        assert "integration-test-topic" in topics


class TestSQSIntegration:
    def test_create_queue_publish_and_consume(self, sqs_factory: SQSFactory) -> None:
        admin = sqs_factory.create_admin()
        admin.create_queue("integration-test-queue")

        producer = sqs_factory.create_producer()
        producer.publish("integration-test-queue", "integration-message")
        producer.close()

        consumer = sqs_factory.create_consumer()
        messages = consumer.consume("integration-test-queue", max_messages=1)
        consumer.close()

        assert messages == ["integration-message"]

        admin.delete_queue("integration-test-queue")
