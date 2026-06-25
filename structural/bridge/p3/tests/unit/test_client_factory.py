"""Unit tests for the client_factory composition root."""

from __future__ import annotations

import pytest

from task_queue.domain.queue_clients import PriorityQueueClient, TaskQueueClient
from task_queue.infrastructure.brokers import InMemoryBroker
from task_queue.infrastructure.client_factory import CLIENT_REGISTRY, build_queue_client


class TestBuildQueueClient:
    def test_builds_task_client_with_memory_broker(self) -> None:
        client = build_queue_client("task", "memory")

        assert isinstance(client, TaskQueueClient)
        assert isinstance(client._broker, InMemoryBroker)

    def test_builds_priority_client(self) -> None:
        client = build_queue_client("priority", "memory")
        assert isinstance(client, PriorityQueueClient)

    def test_raises_value_error_for_unknown_client_type(self) -> None:
        with pytest.raises(ValueError, match="Unsupported client type"):
            build_queue_client("bulk", "memory")

    def test_raises_value_error_for_unknown_broker_type(self) -> None:
        with pytest.raises(ValueError, match="Unsupported broker type"):
            build_queue_client("task", "kafka")

    def test_registry_contains_all_expected_clients(self) -> None:
        assert set(CLIENT_REGISTRY.keys()) == {"task", "priority"}

    def test_client_built_is_fully_functional(self) -> None:
        client = build_queue_client("task", "memory")

        message_id = client.enqueue({"x": 1}, "q")
        messages = client.dequeue("q")

        assert len(messages) == 1
        assert messages[0].message_id == message_id
