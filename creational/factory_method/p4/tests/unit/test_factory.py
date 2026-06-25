"""Unit tests for the Factory Method pattern in P4 — Message Consumer Factory.

All tests run in simulation mode (no real brokers required).
Tests verify:
  - Factory Method contract: each Creator returns a MessageConsumer Protocol
  - OCP: new broker requires zero changes to existing tests
  - DIP: use cases work with any ConsumerFactory (verified via fake)
  - ISP: MessageConsumer protocol has minimal interface
"""
from __future__ import annotations

import json

import pytest

from messaging.application.use_cases import (
    ConsumeMessagesUseCase,
    ListBrokersUseCase,
    StreamMessagesUseCase,
)
from messaging.domain.entities import BrokerType, ConsumeConfig, Message
from messaging.domain.interfaces import ConsumerFactory, MessageConsumer
from messaging.infrastructure.consumers import (
    CONSUMER_FACTORY_REGISTRY,
    KafkaConsumerFactory,
    RabbitMQConsumerFactory,
    SQSConsumerFactory,
)


# ── Factory Method contract tests ─────────────────────────────────────────────

class TestKafkaConsumerFactory:
    def test_create_returns_message_consumer(self, kafka_config: ConsumeConfig) -> None:
        factory = KafkaConsumerFactory()
        consumer = factory.create_consumer(kafka_config)
        assert isinstance(consumer, MessageConsumer)

    def test_broker_name(self) -> None:
        assert KafkaConsumerFactory().get_broker_name() == "Kafka"

    def test_consume_all_returns_messages(self, kafka_config: ConsumeConfig) -> None:
        factory = KafkaConsumerFactory()
        messages = factory.consume_all(kafka_config)
        assert len(messages) == kafka_config.limit
        assert all(isinstance(m, Message) for m in messages)

    def test_message_has_expected_fields(self, kafka_config: ConsumeConfig) -> None:
        factory = KafkaConsumerFactory()
        messages = factory.consume_all(kafka_config)
        msg = messages[0]
        assert msg.topic == kafka_config.topic_or_queue
        assert msg.value  # non-empty bytes
        assert msg.timestamp is not None

    def test_message_value_is_valid_json(self, kafka_config: ConsumeConfig) -> None:
        factory = KafkaConsumerFactory()
        messages = factory.consume_all(kafka_config)
        for msg in messages:
            parsed = json.loads(msg.decode_value())
            assert "event" in parsed


class TestRabbitMQConsumerFactory:
    def test_create_returns_message_consumer(self, rabbitmq_config: ConsumeConfig) -> None:
        factory = RabbitMQConsumerFactory()
        consumer = factory.create_consumer(rabbitmq_config)
        assert isinstance(consumer, MessageConsumer)

    def test_broker_name(self) -> None:
        assert RabbitMQConsumerFactory().get_broker_name() == "RabbitMQ"

    def test_consume_all_returns_messages(self, rabbitmq_config: ConsumeConfig) -> None:
        factory = RabbitMQConsumerFactory()
        messages = factory.consume_all(rabbitmq_config)
        assert len(messages) == rabbitmq_config.limit
        assert all(isinstance(m, Message) for m in messages)

    def test_message_headers_present(self, rabbitmq_config: ConsumeConfig) -> None:
        factory = RabbitMQConsumerFactory()
        messages = factory.consume_all(rabbitmq_config)
        assert messages[0].headers.get("source") == "rabbitmq-sim"


class TestSQSConsumerFactory:
    def test_create_returns_message_consumer(self, sqs_config: ConsumeConfig) -> None:
        factory = SQSConsumerFactory()
        consumer = factory.create_consumer(sqs_config)
        assert isinstance(consumer, MessageConsumer)

    def test_broker_name(self) -> None:
        assert "SQS" in SQSConsumerFactory().get_broker_name()

    def test_consume_all_returns_messages(self, sqs_config: ConsumeConfig) -> None:
        factory = SQSConsumerFactory()
        messages = factory.consume_all(sqs_config)
        assert len(messages) == sqs_config.limit

    def test_message_value_is_valid_json(self, sqs_config: ConsumeConfig) -> None:
        factory = SQSConsumerFactory()
        messages = factory.consume_all(sqs_config)
        for msg in messages:
            parsed = json.loads(msg.decode_value())
            assert "Records" in parsed


# ── OCP — adding broker does not break existing tests ─────────────────────────

class TestConsumerFactoryRegistry:
    def test_all_factories_registered(self) -> None:
        assert set(CONSUMER_FACTORY_REGISTRY.keys()) == {"kafka", "rabbitmq", "sqs"}

    def test_each_factory_produces_valid_consumer(self) -> None:
        config = ConsumeConfig(
            broker=BrokerType.KAFKA,
            topic_or_queue="test",
            limit=1,
        )
        for slug, factory in CONSUMER_FACTORY_REGISTRY.items():
            # Update broker type for each factory
            cfg = ConsumeConfig(
                broker=BrokerType(slug),
                topic_or_queue="test",
                limit=1,
            )
            consumer = factory.create_consumer(cfg)
            assert isinstance(consumer, MessageConsumer), f"{slug} must return MessageConsumer"

    def test_each_factory_can_consume_all(self) -> None:
        for slug, factory in CONSUMER_FACTORY_REGISTRY.items():
            cfg = ConsumeConfig(
                broker=BrokerType(slug),
                topic_or_queue="test-topic",
                limit=2,
            )
            messages = factory.consume_all(cfg)
            assert len(messages) == 2, f"{slug} should return 2 messages"


# ── DIP — use cases work with any ConsumerFactory ────────────────────────────

class FakeConsumerFactory(ConsumerFactory):
    """Test double demonstrating DIP: use cases accept any ConsumerFactory."""

    def create_consumer(self, config: ConsumeConfig) -> MessageConsumer:
        class FakeConsumer:
            def __init__(self, cfg: ConsumeConfig) -> None:
                self._cfg = cfg
                self._connected = False
                self._topic: str | None = None

            def connect(self) -> None:
                self._connected = True

            def subscribe(self, topic_or_queue: str) -> None:
                self._topic = topic_or_queue

            def consume(self):  # type: ignore[override]
                from datetime import datetime, timezone

                limit = self._cfg.limit or 2
                for i in range(limit):
                    yield Message(
                        topic=self._topic or "fake",
                        key=f"fake-key-{i}",
                        value=b'{"fake": true}',
                        timestamp=datetime.now(tz=timezone.utc),
                    )

            def ack(self, message: Message) -> None:
                pass

            def close(self) -> None:
                self._connected = False

        return FakeConsumer(config)  # type: ignore[return-value]

    def get_broker_name(self) -> str:
        return "Fake"


class TestDependencyInversion:
    def test_consume_use_case_accepts_any_factory(self, kafka_config: ConsumeConfig) -> None:
        fake_factory = FakeConsumerFactory()
        use_case = ConsumeMessagesUseCase(fake_factory)
        messages = use_case.execute(kafka_config)
        assert len(messages) == kafka_config.limit
        assert all(isinstance(m, Message) for m in messages)

    def test_stream_use_case_accepts_any_factory(self, kafka_config: ConsumeConfig) -> None:
        fake_factory = FakeConsumerFactory()
        use_case = StreamMessagesUseCase(fake_factory)
        pairs = list(use_case.execute(kafka_config))
        assert len(pairs) == kafka_config.limit
        for msg, consumer in pairs:
            assert isinstance(msg, Message)

    def test_list_brokers_use_case(self) -> None:
        use_case = ListBrokersUseCase(CONSUMER_FACTORY_REGISTRY)
        result = use_case.execute()
        assert len(result) == 3
        slugs = {item["slug"] for item in result}
        assert slugs == {"kafka", "rabbitmq", "sqs"}


# ── Entity tests ──────────────────────────────────────────────────────────────

class TestConsumeConfig:
    def test_defaults(self) -> None:
        config = ConsumeConfig(
            broker=BrokerType.KAFKA,
            topic_or_queue="orders",
        )
        assert config.group_id == "default-group"
        assert config.limit is None
        assert config.auto_ack is True

    def test_custom_values(self) -> None:
        config = ConsumeConfig(
            broker=BrokerType.RABBITMQ,
            topic_or_queue="payments",
            group_id="my-group",
            limit=50,
            timeout_seconds=10.0,
        )
        assert config.limit == 50
        assert config.timeout_seconds == 10.0


class TestMessage:
    def test_decode_value_utf8(self) -> None:
        msg = _make_message(b"hello world")
        assert msg.decode_value() == "hello world"

    def test_immutability(self) -> None:
        msg = _make_message(b"data")
        with pytest.raises(Exception):
            msg.value = b"changed"  # type: ignore[misc]

    def test_headers_default_empty(self) -> None:
        from datetime import datetime, timezone

        msg = Message(
            topic="t",
            key=None,
            value=b"v",
            timestamp=datetime.now(tz=timezone.utc),
        )
        assert msg.headers == {}


def _make_message(value: bytes) -> Message:
    from datetime import datetime, timezone

    return Message(
        topic="test",
        key="key-1",
        value=value,
        timestamp=datetime.now(tz=timezone.utc),
        headers={"x-source": "test"},
    )
