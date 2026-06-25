"""Unit tests for RefinedAbstractions (TaskQueueClient, PriorityQueueClient).

Verifies the Bridge composition: each client delegates transport to the
injected MessageBroker mock while owning its own queueing semantics.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from task_queue.domain.entities import MessagePriority, QueueMessage
from task_queue.domain.interfaces import MessageBroker
from task_queue.domain.queue_clients import PriorityQueueClient, TaskQueueClient


@pytest.fixture
def mock_broker() -> MagicMock:
    broker = MagicMock(spec=MessageBroker)
    broker.get_broker_name.return_value = "RabbitMQ"
    return broker


class TestTaskQueueClient:
    def test_enqueue_publishes_normal_priority_message(
        self, mock_broker: MagicMock
    ) -> None:
        mock_broker.publish.return_value = "id-1"
        client = TaskQueueClient(mock_broker)

        message_id = client.enqueue({"task": "send_email"}, "emails")

        assert message_id == "id-1"
        published_message: QueueMessage = mock_broker.publish.call_args[0][0]
        assert published_message.priority == MessagePriority.NORMAL
        assert published_message.payload == {"task": "send_email"}
        assert published_message.queue_name == "emails"

    def test_dequeue_delegates_to_broker(self, mock_broker: MagicMock) -> None:
        expected = [QueueMessage(queue_name="emails", payload={})]
        mock_broker.consume.return_value = expected

        result = TaskQueueClient(mock_broker).dequeue("emails", max_messages=3)

        assert result == expected
        mock_broker.consume.assert_called_once_with("emails", max_messages=3)

    def test_get_broker_name_delegates_to_broker(self, mock_broker: MagicMock) -> None:
        assert TaskQueueClient(mock_broker).get_broker_name() == "RabbitMQ"


class TestPriorityQueueClient:
    @pytest.mark.parametrize(
        ("raw_priority", "expected"),
        [
            ("high", MessagePriority.HIGH),
            ("critical", MessagePriority.CRITICAL),
            ("low", MessagePriority.LOW),
            ("unknown", MessagePriority.NORMAL),
        ],
    )
    def test_enqueue_resolves_priority_from_payload(
        self, mock_broker: MagicMock, raw_priority: str, expected: MessagePriority
    ) -> None:
        mock_broker.publish.return_value = "id-1"
        client = PriorityQueueClient(mock_broker)

        client.enqueue({"priority": raw_priority}, "alerts")

        published_message: QueueMessage = mock_broker.publish.call_args[0][0]
        assert published_message.priority == expected

    def test_enqueue_uses_default_priority_when_missing(
        self, mock_broker: MagicMock
    ) -> None:
        mock_broker.publish.return_value = "id-1"
        client = PriorityQueueClient(mock_broker, default_priority=MessagePriority.HIGH)

        client.enqueue({}, "alerts")

        published_message: QueueMessage = mock_broker.publish.call_args[0][0]
        assert published_message.priority == MessagePriority.HIGH

    def test_dequeue_delegates_to_broker(self, mock_broker: MagicMock) -> None:
        expected = [QueueMessage(queue_name="alerts", payload={})]
        mock_broker.consume.return_value = expected

        result = PriorityQueueClient(mock_broker).dequeue("alerts")

        assert result == expected
