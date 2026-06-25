"""Unit tests for the Adapter pattern in P5 — Messaging Protocol Adapter.

All tests run in simulation mode (no real RabbitMQ/Kafka required).
Tests verify:
  - Target contract: every Adapter satisfies the MessageBroker Protocol
  - LSP: RabbitMQAdapter and KafkaAdapter are interchangeable
  - OCP: registry-based selection requires no branching in client code
  - DIP: use cases work with any MessageBroker (verified via a fake)
  - Publish AND consume are both supported, in-memory, for both adapters
"""

from __future__ import annotations

import json
from dataclasses import FrozenInstanceError

import pytest

from messaging_adapter.application.use_cases import (
    ConsumeMessagesUseCase,
    ListBrokersUseCase,
    PublishMessageUseCase,
)
from messaging_adapter.domain.entities import (
    BrokerConnectionError,
    BrokerType,
    ConsumeConfig,
    Message,
    PublishConfig,
)
from messaging_adapter.domain.interfaces import MessageBroker
from messaging_adapter.infrastructure.kafka_adapter import KafkaAdapter
from messaging_adapter.infrastructure.rabbitmq_adapter import RabbitMQAdapter
from messaging_adapter.infrastructure.registry import (
    BROKER_DISPLAY_NAMES,
    build_broker_registry,
)

# ── Target contract tests ──────────────────────────────────────────────────────


class TestRabbitMQAdapter:
    def test_satisfies_message_broker_protocol(
        self, rabbitmq_adapter: RabbitMQAdapter
    ) -> None:
        assert isinstance(rabbitmq_adapter, MessageBroker)

    def test_publish_then_consume_roundtrip(
        self,
        rabbitmq_adapter: RabbitMQAdapter,
        rabbitmq_publish_config: PublishConfig,
        rabbitmq_consume_config: ConsumeConfig,
    ) -> None:
        rabbitmq_adapter.connect()
        message = Message(topic=rabbitmq_publish_config.topic, value=b'{"x": 1}')
        rabbitmq_adapter.publish(rabbitmq_publish_config.topic, message)

        consumed = list(rabbitmq_adapter.consume(rabbitmq_consume_config))
        rabbitmq_adapter.close()

        assert len(consumed) == 1
        assert consumed[0].value == b'{"x": 1}'

    def test_publish_without_connect_raises(
        self, rabbitmq_adapter: RabbitMQAdapter
    ) -> None:
        message = Message(topic="payments", value=b"data")
        with pytest.raises(BrokerConnectionError):
            rabbitmq_adapter.publish("payments", message)

    def test_consume_simulated_when_buffer_empty(
        self, rabbitmq_adapter: RabbitMQAdapter, rabbitmq_consume_config: ConsumeConfig
    ) -> None:
        rabbitmq_adapter.connect()
        messages = list(rabbitmq_adapter.consume(rabbitmq_consume_config))
        rabbitmq_adapter.close()

        assert len(messages) == rabbitmq_consume_config.limit
        for msg in messages:
            assert msg.headers.get("source") == "rabbitmq-sim"

    def test_consumed_message_value_is_valid_json(
        self, rabbitmq_adapter: RabbitMQAdapter, rabbitmq_consume_config: ConsumeConfig
    ) -> None:
        rabbitmq_adapter.connect()
        messages = list(rabbitmq_adapter.consume(rabbitmq_consume_config))
        rabbitmq_adapter.close()
        for msg in messages:
            parsed = json.loads(msg.decode_value())
            assert "event" in parsed

    def test_close_is_idempotent_safe(self, rabbitmq_adapter: RabbitMQAdapter) -> None:
        rabbitmq_adapter.connect()
        rabbitmq_adapter.close()
        rabbitmq_adapter.close()  # should not raise


class TestKafkaAdapter:
    def test_satisfies_message_broker_protocol(
        self, kafka_adapter: KafkaAdapter
    ) -> None:
        assert isinstance(kafka_adapter, MessageBroker)

    def test_publish_then_consume_roundtrip(
        self,
        kafka_adapter: KafkaAdapter,
        kafka_publish_config: PublishConfig,
        kafka_consume_config: ConsumeConfig,
    ) -> None:
        kafka_adapter.connect()
        message = Message(topic=kafka_publish_config.topic, value=b'{"y": 2}')
        kafka_adapter.publish(kafka_publish_config.topic, message)

        consumed = list(kafka_adapter.consume(kafka_consume_config))
        kafka_adapter.close()

        assert len(consumed) == 1
        assert consumed[0].value == b'{"y": 2}'

    def test_publish_without_connect_raises(self, kafka_adapter: KafkaAdapter) -> None:
        message = Message(topic="orders", value=b"data")
        with pytest.raises(BrokerConnectionError):
            kafka_adapter.publish("orders", message)

    def test_consume_simulated_when_buffer_empty(
        self, kafka_adapter: KafkaAdapter, kafka_consume_config: ConsumeConfig
    ) -> None:
        kafka_adapter.connect()
        messages = list(kafka_adapter.consume(kafka_consume_config))
        kafka_adapter.close()

        assert len(messages) == kafka_consume_config.limit
        for msg in messages:
            assert msg.headers.get("source") == "kafka-sim"

    def test_consumed_message_value_is_valid_json(
        self, kafka_adapter: KafkaAdapter, kafka_consume_config: ConsumeConfig
    ) -> None:
        kafka_adapter.connect()
        messages = list(kafka_adapter.consume(kafka_consume_config))
        kafka_adapter.close()
        for msg in messages:
            parsed = json.loads(msg.decode_value())
            assert "event" in parsed

    def test_close_is_idempotent_safe(self, kafka_adapter: KafkaAdapter) -> None:
        kafka_adapter.connect()
        kafka_adapter.close()
        kafka_adapter.close()  # should not raise


# ── LSP — adapters are interchangeable ─────────────────────────────────────────


class TestLiskovSubstitution:
    @pytest.mark.parametrize("adapter_cls", [RabbitMQAdapter, KafkaAdapter])
    def test_any_adapter_can_publish_and_consume(self, adapter_cls: type) -> None:
        adapter = adapter_cls()
        config = ConsumeConfig(broker=BrokerType.RABBITMQ, topic="generic", limit=2)

        adapter.connect()
        adapter.publish("generic", Message(topic="generic", value=b"a"))
        adapter.publish("generic", Message(topic="generic", value=b"b"))
        messages = list(adapter.consume(config))
        adapter.close()

        assert len(messages) == 2
        assert {m.value for m in messages} == {b"a", b"b"}


# ── OCP — registry-based selection, no branching ───────────────────────────────


class TestBrokerRegistry:
    def test_all_brokers_registered(self) -> None:
        registry = build_broker_registry()
        assert set(registry.keys()) == {BrokerType.RABBITMQ, BrokerType.KAFKA}

    def test_each_registered_adapter_satisfies_protocol(self) -> None:
        registry = build_broker_registry()
        for broker_type, adapter in registry.items():
            assert isinstance(
                adapter, MessageBroker
            ), f"{broker_type} must satisfy Target"

    def test_display_names_cover_all_brokers(self) -> None:
        assert set(BROKER_DISPLAY_NAMES.keys()) == {
            BrokerType.RABBITMQ,
            BrokerType.KAFKA,
        }


# ── DIP — use cases work with any MessageBroker ────────────────────────────────


class FakeBroker:
    """Test double demonstrating DIP: use cases accept any MessageBroker."""

    def __init__(self) -> None:
        self.connected = False
        self.published: list[Message] = []

    def connect(self) -> None:
        self.connected = True

    def publish(self, topic: str, message: Message) -> None:
        self.published.append(message)

    def consume(self, config: ConsumeConfig):  # type: ignore[no-untyped-def]
        limit = config.limit or 2
        for i in range(limit):
            yield Message(topic=config.topic, value=f"fake-{i}".encode())

    def close(self) -> None:
        self.connected = False


class TestDependencyInversion:
    def test_publish_use_case_accepts_any_broker(
        self, rabbitmq_publish_config: PublishConfig
    ) -> None:
        fake = FakeBroker()
        use_case = PublishMessageUseCase(fake)
        result = use_case.execute(rabbitmq_publish_config, b"payload")

        assert isinstance(result, Message)
        assert fake.published == [result]
        assert fake.connected is False  # closed after execute

    def test_consume_use_case_accepts_any_broker(
        self, rabbitmq_consume_config: ConsumeConfig
    ) -> None:
        fake = FakeBroker()
        use_case = ConsumeMessagesUseCase(fake)
        messages = use_case.execute(rabbitmq_consume_config)

        assert len(messages) == rabbitmq_consume_config.limit
        assert all(isinstance(m, Message) for m in messages)

    def test_list_brokers_use_case(self) -> None:
        use_case = ListBrokersUseCase(BROKER_DISPLAY_NAMES)
        result = use_case.execute()

        slugs = {item["slug"] for item in result}
        assert slugs == {"rabbitmq", "kafka"}


# ── Entity tests ────────────────────────────────────────────────────────────────


class TestMessage:
    def test_decode_value_utf8(self) -> None:
        msg = Message(topic="t", value=b"hello world")
        assert msg.decode_value() == "hello world"

    def test_immutability(self) -> None:
        msg = Message(topic="t", value=b"data")
        with pytest.raises(FrozenInstanceError):
            msg.value = b"changed"  # type: ignore[misc]

    def test_headers_default_empty(self) -> None:
        msg = Message(topic="t", value=b"v")
        assert msg.headers == {}


class TestPublishConfig:
    def test_defaults(self) -> None:
        config = PublishConfig(broker=BrokerType.KAFKA, topic="orders")
        assert config.headers == {}
        assert config.key is None


class TestConsumeConfig:
    def test_defaults(self) -> None:
        config = ConsumeConfig(broker=BrokerType.RABBITMQ, topic="payments")
        assert config.group_id == "default-group"
        assert config.limit is None
        assert config.timeout_seconds == 5.0
