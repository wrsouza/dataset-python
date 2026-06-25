"""Unit tests for ConcreteProducts using mocked broker SDK clients.

These tests exercise RabbitMQProducer/Consumer/QueueAdmin, KafkaProducer/
Consumer/QueueAdmin and SQSProducer/Consumer/QueueAdmin without requiring
live broker connections, by monkeypatching the imported SDK modules.
"""

from __future__ import annotations

import sys
import types
from unittest.mock import MagicMock

import pytest

from broker_factory.infrastructure.factories import (
    KafkaConsumer,
    KafkaProducer,
    KafkaQueueAdmin,
    RabbitMQConsumer,
    RabbitMQProducer,
    RabbitMQQueueAdmin,
    SQSConsumer,
    SQSProducer,
    SQSQueueAdmin,
)


@pytest.fixture
def fake_pika(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Install a fake `pika` module so RabbitMQ products can be unit tested."""
    fake_module = types.ModuleType("pika")
    fake_module.URLParameters = MagicMock(return_value="params")  # type: ignore[attr-defined]
    connection = MagicMock()
    connection.is_closed = False
    connection.__enter__ = MagicMock(return_value=connection)
    connection.__exit__ = MagicMock(return_value=False)
    fake_module.BlockingConnection = MagicMock(return_value=connection)  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "pika", fake_module)
    return connection


class TestRabbitMQProducer:
    def test_publish_declares_queue_and_publishes(self, fake_pika: MagicMock) -> None:
        producer = RabbitMQProducer(connection_url="amqp://test")

        producer.publish("orders", "hello")

        channel = fake_pika.channel()
        channel.queue_declare.assert_called_with(queue="orders", durable=True)
        channel.basic_publish.assert_called_once()

    def test_close_closes_open_connection(self, fake_pika: MagicMock) -> None:
        producer = RabbitMQProducer(connection_url="amqp://test")

        producer.close()

        fake_pika.close.assert_called_once()

    def test_close_skips_already_closed_connection(self, fake_pika: MagicMock) -> None:
        fake_pika.is_closed = True
        producer = RabbitMQProducer(connection_url="amqp://test")

        producer.close()

        fake_pika.close.assert_not_called()


class TestRabbitMQConsumer:
    def test_consume_returns_messages_until_empty(self, fake_pika: MagicMock) -> None:
        channel = fake_pika.channel()
        channel.basic_get.side_effect = [
            ("method", "props", b"msg-1"),
            (None, None, None),
        ]
        consumer = RabbitMQConsumer(connection_url="amqp://test")

        messages = consumer.consume("orders", max_messages=5)

        assert messages == ["msg-1"]

    def test_acknowledge_and_close_are_noops(self, fake_pika: MagicMock) -> None:
        consumer = RabbitMQConsumer(connection_url="amqp://test")

        consumer.acknowledge("msg-id")
        consumer.close()


class TestRabbitMQQueueAdmin:
    def test_create_queue_returns_amqp_url(self, fake_pika: MagicMock) -> None:
        admin = RabbitMQQueueAdmin(connection_url="amqp://test")

        identifier = admin.create_queue("orders")

        assert identifier == "amqp://orders"

    def test_delete_queue_calls_queue_delete(self, fake_pika: MagicMock) -> None:
        admin = RabbitMQQueueAdmin(connection_url="amqp://test")

        admin.delete_queue("orders")

        fake_pika.channel().queue_delete.assert_called_with(queue="orders")

    def test_list_queues_returns_empty_placeholder(self, fake_pika: MagicMock) -> None:
        admin = RabbitMQQueueAdmin(connection_url="amqp://test")

        assert admin.list_queues() == []


@pytest.fixture
def fake_kafka(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Install a fake `kafka` module so Kafka products can be unit tested."""
    fake_module = types.ModuleType("kafka")
    producer_instance = MagicMock()
    consumer_instance = MagicMock()
    consumer_instance.__iter__ = MagicMock(return_value=iter([]))
    fake_module.KafkaProducer = MagicMock(return_value=producer_instance)  # type: ignore[attr-defined]
    fake_module.KafkaConsumer = MagicMock(return_value=consumer_instance)  # type: ignore[attr-defined]

    fake_admin_module = types.ModuleType("kafka.admin")
    admin_instance = MagicMock()
    fake_admin_module.KafkaAdminClient = MagicMock(return_value=admin_instance)  # type: ignore[attr-defined]
    fake_admin_module.NewTopic = MagicMock()  # type: ignore[attr-defined]

    monkeypatch.setitem(sys.modules, "kafka", fake_module)
    monkeypatch.setitem(sys.modules, "kafka.admin", fake_admin_module)
    return admin_instance


class TestKafkaProducer:
    def test_publish_sends_and_flushes(self, fake_kafka: MagicMock) -> None:
        producer = KafkaProducer(bootstrap_servers="kafka:9092")

        producer.publish("orders", "hello")

        underlying = producer._get_producer()
        underlying.send.assert_called_with("orders", "hello")
        underlying.flush.assert_called()

    def test_close_releases_producer(self, fake_kafka: MagicMock) -> None:
        producer = KafkaProducer(bootstrap_servers="kafka:9092")
        producer.publish("orders", "hello")

        producer.close()

        assert producer._producer is None


class TestKafkaConsumer:
    def test_consume_returns_empty_when_no_messages(
        self, fake_kafka: MagicMock
    ) -> None:
        consumer = KafkaConsumer(bootstrap_servers="kafka:9092")

        messages = consumer.consume("orders", max_messages=5)

        assert messages == []

    def test_acknowledge_is_noop(self, fake_kafka: MagicMock) -> None:
        consumer = KafkaConsumer(bootstrap_servers="kafka:9092")

        consumer.acknowledge("msg-id")

    def test_close_without_active_consumer_is_safe(self, fake_kafka: MagicMock) -> None:
        consumer = KafkaConsumer(bootstrap_servers="kafka:9092")

        consumer.close()


class TestKafkaQueueAdmin:
    def test_create_queue_returns_kafka_url(self, fake_kafka: MagicMock) -> None:
        admin = KafkaQueueAdmin(bootstrap_servers="kafka:9092")

        identifier = admin.create_queue("orders")

        assert identifier == "kafka://orders"
        fake_kafka.close.assert_called()

    def test_create_queue_swallows_topic_exists_error(
        self, fake_kafka: MagicMock
    ) -> None:
        fake_kafka.create_topics.side_effect = RuntimeError("already exists")
        admin = KafkaQueueAdmin(bootstrap_servers="kafka:9092")

        identifier = admin.create_queue("orders")

        assert identifier == "kafka://orders"

    def test_delete_queue_calls_delete_topics(self, fake_kafka: MagicMock) -> None:
        admin = KafkaQueueAdmin(bootstrap_servers="kafka:9092")

        admin.delete_queue("orders")

        fake_kafka.delete_topics.assert_called_with(["orders"])

    def test_list_queues_filters_internal_topics(self, fake_kafka: MagicMock) -> None:
        fake_kafka.list_topics.return_value = ["orders", "__consumer_offsets"]
        admin = KafkaQueueAdmin(bootstrap_servers="kafka:9092")

        topics = admin.list_queues()

        assert topics == ["orders"]


@pytest.fixture
def fake_sqs_client() -> MagicMock:
    return MagicMock()


class TestSQSProducer:
    def test_publish_sends_message_to_resolved_queue_url(
        self, fake_sqs_client: MagicMock
    ) -> None:
        fake_sqs_client.get_queue_url.return_value = {
            "QueueUrl": "http://localstack/orders"
        }
        producer = SQSProducer(sqs_client=fake_sqs_client)

        producer.publish("orders", "hello")

        fake_sqs_client.send_message.assert_called_with(
            QueueUrl="http://localstack/orders", MessageBody="hello"
        )

    def test_close_is_noop(self, fake_sqs_client: MagicMock) -> None:
        SQSProducer(sqs_client=fake_sqs_client).close()


class TestSQSConsumer:
    def test_consume_returns_messages_and_deletes_them(
        self, fake_sqs_client: MagicMock
    ) -> None:
        fake_sqs_client.get_queue_url.return_value = {
            "QueueUrl": "http://localstack/orders"
        }
        fake_sqs_client.receive_message.return_value = {
            "Messages": [{"Body": "hello", "ReceiptHandle": "abc"}]
        }
        consumer = SQSConsumer(sqs_client=fake_sqs_client)

        messages = consumer.consume("orders", max_messages=20)

        assert messages == ["hello"]
        fake_sqs_client.delete_message.assert_called_with(
            QueueUrl="http://localstack/orders", ReceiptHandle="abc"
        )

    def test_consume_returns_empty_when_no_messages(
        self, fake_sqs_client: MagicMock
    ) -> None:
        fake_sqs_client.get_queue_url.return_value = {
            "QueueUrl": "http://localstack/orders"
        }
        fake_sqs_client.receive_message.return_value = {}
        consumer = SQSConsumer(sqs_client=fake_sqs_client)

        assert consumer.consume("orders", max_messages=1) == []

    def test_acknowledge_and_close_are_noops(self, fake_sqs_client: MagicMock) -> None:
        consumer = SQSConsumer(sqs_client=fake_sqs_client)

        consumer.acknowledge("msg-id")
        consumer.close()


class TestSQSQueueAdmin:
    def test_create_queue_returns_queue_url(self, fake_sqs_client: MagicMock) -> None:
        fake_sqs_client.create_queue.return_value = {
            "QueueUrl": "http://localstack/orders"
        }
        admin = SQSQueueAdmin(sqs_client=fake_sqs_client)

        assert admin.create_queue("orders") == "http://localstack/orders"

    def test_delete_queue_resolves_url_then_deletes(
        self, fake_sqs_client: MagicMock
    ) -> None:
        fake_sqs_client.get_queue_url.return_value = {
            "QueueUrl": "http://localstack/orders"
        }
        admin = SQSQueueAdmin(sqs_client=fake_sqs_client)

        admin.delete_queue("orders")

        fake_sqs_client.delete_queue.assert_called_with(
            QueueUrl="http://localstack/orders"
        )

    def test_list_queues_extracts_names_from_urls(
        self, fake_sqs_client: MagicMock
    ) -> None:
        fake_sqs_client.list_queues.return_value = {
            "QueueUrls": [
                "http://localstack/orders",
                "http://localstack/payments",
            ]
        }
        admin = SQSQueueAdmin(sqs_client=fake_sqs_client)

        assert admin.list_queues() == ["orders", "payments"]

    def test_list_queues_returns_empty_when_no_urls(
        self, fake_sqs_client: MagicMock
    ) -> None:
        fake_sqs_client.list_queues.return_value = {}
        admin = SQSQueueAdmin(sqs_client=fake_sqs_client)

        assert admin.list_queues() == []
