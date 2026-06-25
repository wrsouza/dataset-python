"""Unit tests for the three ConcreteImplementors: CeleryRedis, RabbitMQ, SQS.

Real network calls are never made — each external client (redis, pika,
boto3) is mocked at the point brokers.py imports it.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from task_queue.domain.entities import (
    BrokerConnectionError,
    BrokerPublishError,
    QueueMessage,
)
from task_queue.infrastructure.brokers import (
    BROKER_REGISTRY,
    CeleryRedisBroker,
    InMemoryBroker,
    RabbitMQBroker,
    SQSBroker,
    get_broker,
)


class TestCeleryRedisBroker:
    def test_publish_pushes_serialised_message_and_returns_id(self) -> None:
        broker = CeleryRedisBroker()
        message = QueueMessage(queue_name="emails", payload={"to": "a@b.com"})

        with patch("redis.Redis.from_url") as from_url:
            mock_redis = MagicMock()
            from_url.return_value = mock_redis

            message_id = broker.publish(message)

        assert message_id == message.message_id
        mock_redis.lpush.assert_called_once()
        queue_arg, body_arg = mock_redis.lpush.call_args[0]
        assert queue_arg == "emails"
        assert json.loads(body_arg)["message_id"] == message.message_id

    def test_publish_wraps_exception_in_broker_publish_error(self) -> None:
        broker = CeleryRedisBroker()
        message = QueueMessage(queue_name="emails", payload={})

        with patch("redis.Redis.from_url", side_effect=RuntimeError("boom")):
            with pytest.raises(BrokerPublishError):
                broker.publish(message)

    def test_consume_pops_and_deserialises_messages(self) -> None:
        broker = CeleryRedisBroker()
        stored = QueueMessage(queue_name="emails", payload={"x": 1})

        with patch("redis.Redis.from_url") as from_url:
            mock_redis = MagicMock()
            mock_redis.rpop.side_effect = [
                json.dumps(stored.to_dict()).encode(),
                None,
            ]
            from_url.return_value = mock_redis

            messages = broker.consume("emails", max_messages=2)

        assert len(messages) == 1
        assert messages[0].payload == {"x": 1}

    def test_consume_wraps_exception_in_broker_connection_error(self) -> None:
        broker = CeleryRedisBroker()

        with patch("redis.Redis.from_url", side_effect=RuntimeError("down")):
            with pytest.raises(BrokerConnectionError):
                broker.consume("emails")

    def test_health_check_reports_healthy_on_pong(self) -> None:
        broker = CeleryRedisBroker()

        with patch("redis.Redis.from_url") as from_url:
            mock_redis = MagicMock()
            mock_redis.ping.return_value = True
            from_url.return_value = mock_redis

            result = broker.health_check()

        assert result.is_healthy is True
        assert result.broker == "CeleryRedis"

    def test_health_check_reports_unhealthy_on_exception(self) -> None:
        broker = CeleryRedisBroker()

        with patch("redis.Redis.from_url", side_effect=RuntimeError("no conn")):
            result = broker.health_check()

        assert result.is_healthy is False
        assert result.error_message == "no conn"

    def test_acknowledge_always_true(self) -> None:
        assert CeleryRedisBroker().acknowledge("any-id") is True

    def test_get_broker_name(self) -> None:
        assert CeleryRedisBroker().get_broker_name() == "CeleryRedis"

    def test_redact_hides_credentials(self) -> None:
        assert CeleryRedisBroker._redact("redis://user:pw@host:6379/0") == "host:6379/0"
        assert CeleryRedisBroker._redact("redis://host:6379/0") == "redis://host:6379/0"


class TestRabbitMQBroker:
    def test_publish_declares_queue_and_publishes(self) -> None:
        broker = RabbitMQBroker()
        message = QueueMessage(queue_name="orders", payload={"id": 1})

        with (
            patch("pika.BlockingConnection") as blocking_connection,
            patch("pika.PlainCredentials"),
            patch("pika.ConnectionParameters"),
        ):
            mock_channel = MagicMock()
            mock_connection = MagicMock()
            mock_connection.channel.return_value = mock_channel
            blocking_connection.return_value = mock_connection

            message_id = broker.publish(message)

        assert message_id == message.message_id
        mock_channel.queue_declare.assert_called_once_with(queue="orders", durable=True)
        mock_channel.basic_publish.assert_called_once()

    def test_publish_wraps_exception_in_broker_publish_error(self) -> None:
        broker = RabbitMQBroker()
        message = QueueMessage(queue_name="orders", payload={})

        with patch("pika.BlockingConnection", side_effect=RuntimeError("refused")):
            with pytest.raises(BrokerPublishError):
                broker.publish(message)

    def test_consume_gets_messages_until_none(self) -> None:
        broker = RabbitMQBroker()
        stored = QueueMessage(queue_name="orders", payload={"id": 1})

        with patch("pika.BlockingConnection") as blocking_connection:
            mock_channel = MagicMock()
            mock_channel.basic_get.side_effect = [
                (MagicMock(), MagicMock(), json.dumps(stored.to_dict()).encode()),
                (None, None, None),
            ]
            mock_connection = MagicMock()
            mock_connection.channel.return_value = mock_channel
            blocking_connection.return_value = mock_connection

            messages = broker.consume("orders", max_messages=2)

        assert len(messages) == 1
        assert messages[0].payload == {"id": 1}

    def test_consume_wraps_exception_in_broker_connection_error(self) -> None:
        broker = RabbitMQBroker()

        with patch("pika.BlockingConnection", side_effect=RuntimeError("down")):
            with pytest.raises(BrokerConnectionError):
                broker.consume("orders")

    def test_health_check_reports_open_connection(self) -> None:
        broker = RabbitMQBroker()

        with patch("pika.BlockingConnection") as blocking_connection:
            mock_connection = MagicMock()
            mock_connection.is_open = True
            blocking_connection.return_value = mock_connection

            result = broker.health_check()

        assert result.is_healthy is True
        assert result.broker == "RabbitMQ"

    def test_health_check_reports_unhealthy_on_exception(self) -> None:
        broker = RabbitMQBroker()

        with patch("pika.BlockingConnection", side_effect=RuntimeError("no conn")):
            result = broker.health_check()

        assert result.is_healthy is False

    def test_acknowledge_always_true(self) -> None:
        assert RabbitMQBroker().acknowledge("any-id") is True

    def test_get_broker_name(self) -> None:
        assert RabbitMQBroker().get_broker_name() == "RabbitMQ"


class TestSQSBroker:
    def setup_method(self) -> None:
        # Clear the class-level queue URL cache between tests.
        SQSBroker._queue_urls.clear()

    def test_publish_sends_message_and_returns_id(self) -> None:
        broker = SQSBroker()
        message = QueueMessage(queue_name="orders", payload={"id": 1})

        with patch("boto3.client") as boto_client:
            mock_client = MagicMock()
            mock_client.get_queue_url.return_value = {
                "QueueUrl": "http://localstack:4566/000/orders"
            }
            boto_client.return_value = mock_client

            message_id = broker.publish(message)

        assert message_id == message.message_id
        mock_client.send_message.assert_called_once()

    def test_publish_creates_queue_when_missing(self) -> None:
        broker = SQSBroker()
        message = QueueMessage(queue_name="new-queue", payload={})

        with patch("boto3.client") as boto_client:
            mock_client = MagicMock()
            mock_client.get_queue_url.side_effect = RuntimeError("does not exist")
            mock_client.create_queue.return_value = {
                "QueueUrl": "http://localstack:4566/000/new-queue"
            }
            boto_client.return_value = mock_client

            broker.publish(message)

        mock_client.create_queue.assert_called_once_with(QueueName="new-queue")

    def test_publish_wraps_exception_in_broker_publish_error(self) -> None:
        broker = SQSBroker()
        message = QueueMessage(queue_name="orders", payload={})

        with patch("boto3.client", side_effect=RuntimeError("boom")):
            with pytest.raises(BrokerPublishError):
                broker.publish(message)

    def test_consume_receives_and_deletes_messages(self) -> None:
        broker = SQSBroker()
        stored = QueueMessage(queue_name="orders", payload={"id": 1})

        with patch("boto3.client") as boto_client:
            mock_client = MagicMock()
            mock_client.get_queue_url.return_value = {
                "QueueUrl": "http://localstack:4566/000/orders"
            }
            mock_client.receive_message.return_value = {
                "Messages": [
                    {
                        "Body": json.dumps(stored.to_dict()),
                        "ReceiptHandle": "handle-1",
                    }
                ]
            }
            boto_client.return_value = mock_client

            messages = broker.consume("orders", max_messages=1)

        assert len(messages) == 1
        assert messages[0].payload == {"id": 1}
        mock_client.delete_message.assert_called_once()

    def test_consume_wraps_exception_in_broker_connection_error(self) -> None:
        broker = SQSBroker()

        with patch("boto3.client", side_effect=RuntimeError("down")):
            with pytest.raises(BrokerConnectionError):
                broker.consume("orders")

    def test_health_check_reports_healthy(self) -> None:
        broker = SQSBroker()

        with patch("boto3.client") as boto_client:
            boto_client.return_value = MagicMock()
            result = broker.health_check()

        assert result.is_healthy is True
        assert result.broker == "SQS"

    def test_health_check_reports_unhealthy_on_exception(self) -> None:
        broker = SQSBroker()

        with patch("boto3.client", side_effect=RuntimeError("no conn")):
            result = broker.health_check()

        assert result.is_healthy is False

    def test_acknowledge_always_true(self) -> None:
        assert SQSBroker().acknowledge("any-id") is True

    def test_get_broker_name(self) -> None:
        assert SQSBroker().get_broker_name() == "SQS"


class TestInMemoryBroker:
    def test_publish_then_consume_round_trip(self) -> None:
        broker = InMemoryBroker()
        message = QueueMessage(queue_name="q", payload={"a": 1})

        message_id = broker.publish(message)
        consumed = broker.consume("q", max_messages=1)

        assert message_id == message.message_id
        assert consumed == [message]

    def test_consume_returns_empty_list_when_queue_empty(self) -> None:
        broker = InMemoryBroker()
        assert broker.consume("missing") == []

    def test_health_check_always_healthy(self) -> None:
        result = InMemoryBroker().health_check()
        assert result.is_healthy is True
        assert result.broker == "InMemory"

    def test_acknowledge_always_true(self) -> None:
        assert InMemoryBroker().acknowledge("any-id") is True


class TestBrokerRegistry:
    def test_get_broker_returns_correct_instance(self) -> None:
        assert isinstance(get_broker("celery_redis"), CeleryRedisBroker)
        assert isinstance(get_broker("rabbitmq"), RabbitMQBroker)
        assert isinstance(get_broker("sqs"), SQSBroker)
        assert isinstance(get_broker("memory"), InMemoryBroker)

    def test_get_broker_is_case_insensitive(self) -> None:
        assert isinstance(get_broker("SQS"), SQSBroker)

    def test_get_broker_raises_value_error_for_unknown_broker(self) -> None:
        with pytest.raises(ValueError, match="Unsupported broker type"):
            get_broker("kafka")

    def test_registry_contains_all_expected_brokers(self) -> None:
        assert set(BROKER_REGISTRY.keys()) == {
            "celery_redis",
            "rabbitmq",
            "sqs",
            "memory",
        }
