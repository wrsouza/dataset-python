"""Unit tests for application use cases using the in-memory broker factory.

No external services required — InMemoryBrokerFactory is a self-contained
fake ConcreteFactory (see tests/conftest.py).
"""

from __future__ import annotations

from broker_factory.application.use_cases import (
    ConsumeMessagesUseCase,
    CreateQueueUseCase,
    ListQueuesUseCase,
    PublishMessageUseCase,
)
from broker_factory.domain.entities import BrokerMessage, ConsumedMessages
from broker_factory.infrastructure.factories import InMemoryBrokerFactory


class TestPublishMessageUseCase:
    def test_publish_returns_broker_message(
        self, in_memory_factory: InMemoryBrokerFactory
    ) -> None:
        use_case = PublishMessageUseCase(in_memory_factory)

        result = use_case.execute("orders", "hello world")

        assert isinstance(result, BrokerMessage)
        assert result.content == "hello world"
        assert result.destination == "orders"
        assert result.broker == "in-memory"

    def test_publish_stores_message_for_later_consumption(
        self, in_memory_factory: InMemoryBrokerFactory
    ) -> None:
        publish_use_case = PublishMessageUseCase(in_memory_factory)
        consume_use_case = ConsumeMessagesUseCase(in_memory_factory)

        publish_use_case.execute("orders", "order-1")

        consumed = consume_use_case.execute("orders")

        assert consumed.messages == ["order-1"]


class TestConsumeMessagesUseCase:
    def test_consume_returns_empty_when_no_messages(
        self, in_memory_factory: InMemoryBrokerFactory
    ) -> None:
        use_case = ConsumeMessagesUseCase(in_memory_factory)

        result = use_case.execute("empty-queue")

        assert isinstance(result, ConsumedMessages)
        assert result.messages == []
        assert result.count == 0
        assert result.broker == "in-memory"

    def test_consume_respects_max_messages(
        self, in_memory_factory: InMemoryBrokerFactory
    ) -> None:
        publish_use_case = PublishMessageUseCase(in_memory_factory)
        for i in range(5):
            publish_use_case.execute("orders", f"order-{i}")

        consume_use_case = ConsumeMessagesUseCase(in_memory_factory)
        result = consume_use_case.execute("orders", max_messages=2)

        assert result.count == 2
        assert result.messages == ["order-0", "order-1"]


class TestCreateQueueUseCase:
    def test_create_queue_returns_identifier(
        self, in_memory_factory: InMemoryBrokerFactory
    ) -> None:
        use_case = CreateQueueUseCase(in_memory_factory)

        result = use_case.execute("payments")

        assert result["name"] == "payments"
        assert result["broker"] == "in-memory"
        assert result["identifier"] == "in-memory://payments"


class TestListQueuesUseCase:
    def test_list_queues_returns_created_queues(
        self, in_memory_factory: InMemoryBrokerFactory
    ) -> None:
        create_use_case = CreateQueueUseCase(in_memory_factory)
        create_use_case.execute("payments")
        create_use_case.execute("orders")

        list_use_case = ListQueuesUseCase(in_memory_factory)
        result = list_use_case.execute()

        assert result["broker"] == "in-memory"
        assert result["count"] == 2
        assert result["queues"] == ["orders", "payments"]

    def test_list_queues_empty_when_none_created(
        self, in_memory_factory: InMemoryBrokerFactory
    ) -> None:
        use_case = ListQueuesUseCase(in_memory_factory)

        result = use_case.execute()

        assert result["queues"] == []
        assert result["count"] == 0
