"""Unit tests for domain entities and exceptions."""

from __future__ import annotations

import pytest

from broker_factory.domain.entities import (
    BrokerConnectionError,
    BrokerMessage,
    ConsumedMessages,
    QueueNotFoundError,
)


class TestBrokerMessage:
    def test_to_dict_contains_all_fields(self) -> None:
        message = BrokerMessage(
            content="hello",
            destination="orders",
            broker="rabbitmq",
        )

        result = message.to_dict()

        assert result["content"] == "hello"
        assert result["destination"] == "orders"
        assert result["broker"] == "rabbitmq"
        assert "published_at" in result

    def test_is_immutable(self) -> None:
        message = BrokerMessage(content="hello", destination="orders", broker="kafka")

        with pytest.raises(AttributeError):
            message.content = "changed"  # type: ignore[misc]


class TestConsumedMessages:
    def test_to_dict_contains_all_fields(self) -> None:
        consumed = ConsumedMessages(
            source="orders",
            broker="sqs",
            messages=["a", "b"],
            count=2,
        )

        result = consumed.to_dict()

        assert result["source"] == "orders"
        assert result["broker"] == "sqs"
        assert result["messages"] == ["a", "b"]
        assert result["count"] == 2


class TestBrokerConnectionError:
    def test_message_includes_broker_and_reason(self) -> None:
        error = BrokerConnectionError(broker="kafka", reason="timeout")

        assert error.broker == "kafka"
        assert error.reason == "timeout"
        assert "kafka" in str(error)
        assert "timeout" in str(error)


class TestQueueNotFoundError:
    def test_message_includes_name_and_broker(self) -> None:
        error = QueueNotFoundError(name="orders", broker="rabbitmq")

        assert error.name == "orders"
        assert error.broker == "rabbitmq"
        assert "orders" in str(error)
        assert "rabbitmq" in str(error)
