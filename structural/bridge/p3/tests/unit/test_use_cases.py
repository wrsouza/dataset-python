"""Unit tests for task_queue application use cases.

No real brokers are required — all dependencies are mocked via
unittest.mock.MagicMock with `spec=` for interface compliance.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from task_queue.application.use_cases import (
    CheckBrokerHealthUseCase,
    DequeueMessagesUseCase,
    EnqueueMessageUseCase,
)
from task_queue.domain.entities import (
    BrokerHealth,
    DequeueResult,
    EnqueueResult,
    QueueMessage,
)
from task_queue.domain.interfaces import QueueClient


@pytest.fixture
def mock_client() -> MagicMock:
    client = MagicMock(spec=QueueClient)
    client.get_broker_name.return_value = "CeleryRedis"
    return client


class TestEnqueueMessageUseCase:
    """DIP: depends only on QueueClient, never on a concrete broker."""

    def test_returns_enqueue_result_with_message_id(
        self, mock_client: MagicMock
    ) -> None:
        mock_client.enqueue.return_value = "msg-123"

        result = EnqueueMessageUseCase(mock_client).execute(
            payload={"a": 1}, queue_name="orders"
        )

        assert isinstance(result, EnqueueResult)
        assert result.message_id == "msg-123"
        assert result.queue_name == "orders"
        assert result.broker == "CeleryRedis"

    def test_passes_payload_and_queue_name_to_client(
        self, mock_client: MagicMock
    ) -> None:
        mock_client.enqueue.return_value = "msg-1"

        EnqueueMessageUseCase(mock_client).execute(
            payload={"x": "y"}, queue_name="emails"
        )

        mock_client.enqueue.assert_called_once_with({"x": "y"}, "emails")


class TestDequeueMessagesUseCase:
    """SRP: dequeue orchestration only — no enqueue, no health check."""

    def test_returns_dequeue_result_with_messages(self, mock_client: MagicMock) -> None:
        message = QueueMessage(queue_name="orders", payload={"id": 1})
        mock_client.dequeue.return_value = [message]

        result = DequeueMessagesUseCase(mock_client).execute(
            queue_name="orders", max_messages=1
        )

        assert isinstance(result, DequeueResult)
        assert result.message_count == 1
        assert result.messages[0]["payload"] == {"id": 1}

    def test_returns_empty_result_when_no_messages(
        self, mock_client: MagicMock
    ) -> None:
        mock_client.dequeue.return_value = []

        result = DequeueMessagesUseCase(mock_client).execute(queue_name="orders")

        assert result.message_count == 0
        assert result.messages == []

    def test_passes_max_messages_to_client(self, mock_client: MagicMock) -> None:
        mock_client.dequeue.return_value = []

        DequeueMessagesUseCase(mock_client).execute(queue_name="orders", max_messages=5)

        mock_client.dequeue.assert_called_once_with("orders", max_messages=5)


class TestCheckBrokerHealthUseCase:
    """SRP: health check only; must never propagate broker exceptions."""

    def test_returns_health_result_when_healthy(self, mock_client: MagicMock) -> None:
        mock_client.check_health.return_value = BrokerHealth(
            broker="CeleryRedis", is_healthy=True
        )

        result = CheckBrokerHealthUseCase(mock_client).execute()

        assert isinstance(result, BrokerHealth)
        assert result.is_healthy is True

    def test_never_raises_when_client_throws(self, mock_client: MagicMock) -> None:
        mock_client.check_health.side_effect = RuntimeError("connection refused")

        result = CheckBrokerHealthUseCase(mock_client).execute()

        assert result.is_healthy is False
        assert result.error_message == "connection refused"
        assert result.broker == "CeleryRedis"


class TestDependencyInversion:
    """DIP: use cases behave identically regardless of which client is injected."""

    @pytest.mark.parametrize("broker_name", ["CeleryRedis", "RabbitMQ", "SQS"])
    def test_enqueue_works_with_any_broker_name(self, broker_name: str) -> None:
        client = MagicMock(spec=QueueClient)
        client.get_broker_name.return_value = broker_name
        client.enqueue.return_value = "msg-1"

        result = EnqueueMessageUseCase(client).execute(payload={}, queue_name="q")

        assert result.broker == broker_name
