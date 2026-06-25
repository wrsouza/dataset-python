"""Unit tests for the Abstract Factory implementation (concrete factories).

Verifies that each ConcreteFactory builds the right product family and that
all factories honor the MessageBrokerFactory abstraction (LSP/OCP).
"""

from __future__ import annotations

import pytest

from broker_factory.infrastructure.factories import (
    InMemoryBrokerFactory,
    InMemoryConsumer,
    InMemoryProducer,
    InMemoryQueueAdmin,
    KafkaConsumer,
    KafkaFactory,
    KafkaProducer,
    KafkaQueueAdmin,
    RabbitMQConsumer,
    RabbitMQFactory,
    RabbitMQQueueAdmin,
    SQSConsumer,
    SQSFactory,
    SQSProducer,
    SQSQueueAdmin,
    build_broker_factory,
)


class TestInMemoryBrokerFactory:
    def test_get_broker_name(self) -> None:
        factory = InMemoryBrokerFactory(broker_name="in-memory")

        assert factory.get_broker_name() == "in-memory"

    def test_create_producer_returns_in_memory_producer(self) -> None:
        factory = InMemoryBrokerFactory()

        assert isinstance(factory.create_producer(), InMemoryProducer)

    def test_create_consumer_returns_in_memory_consumer(self) -> None:
        factory = InMemoryBrokerFactory()

        assert isinstance(factory.create_consumer(), InMemoryConsumer)

    def test_create_admin_returns_in_memory_admin(self) -> None:
        factory = InMemoryBrokerFactory()

        assert isinstance(factory.create_admin(), InMemoryQueueAdmin)

    def test_producer_and_consumer_share_same_store(self) -> None:
        factory = InMemoryBrokerFactory()
        producer = factory.create_producer()
        consumer = factory.create_consumer()

        producer.publish("queue-a", "msg")

        assert consumer.consume("queue-a", 10) == ["msg"]


class TestInMemoryQueueAdmin:
    def test_create_then_list_then_delete_queue(self) -> None:
        factory = InMemoryBrokerFactory()
        admin = factory.create_admin()

        identifier = admin.create_queue("orders")

        assert identifier == "in-memory://orders"
        assert admin.list_queues() == ["orders"]

        admin.delete_queue("orders")

        assert admin.list_queues() == []


class TestRabbitMQFactory:
    def test_get_broker_name(self) -> None:
        factory = RabbitMQFactory(connection_url="amqp://test")

        assert factory.get_broker_name() == "rabbitmq"

    def test_create_consumer_returns_rabbitmq_consumer(self) -> None:
        factory = RabbitMQFactory(connection_url="amqp://test")

        assert isinstance(factory.create_consumer(), RabbitMQConsumer)

    def test_create_admin_returns_rabbitmq_admin(self) -> None:
        factory = RabbitMQFactory(connection_url="amqp://test")

        assert isinstance(factory.create_admin(), RabbitMQQueueAdmin)


class TestKafkaFactory:
    def test_get_broker_name(self) -> None:
        factory = KafkaFactory(bootstrap_servers="kafka:9092")

        assert factory.get_broker_name() == "kafka"

    def test_create_producer_returns_kafka_producer(self) -> None:
        factory = KafkaFactory(bootstrap_servers="kafka:9092")

        assert isinstance(factory.create_producer(), KafkaProducer)

    def test_create_consumer_returns_kafka_consumer(self) -> None:
        factory = KafkaFactory(bootstrap_servers="kafka:9092")

        assert isinstance(factory.create_consumer(), KafkaConsumer)

    def test_create_admin_returns_kafka_admin(self) -> None:
        factory = KafkaFactory(bootstrap_servers="kafka:9092")

        assert isinstance(factory.create_admin(), KafkaQueueAdmin)


class TestSQSFactory:
    def test_get_broker_name(self) -> None:
        factory = SQSFactory(endpoint_url="http://localstack:4566")

        assert factory.get_broker_name() == "sqs"

    def test_create_producer_returns_sqs_producer(self) -> None:
        factory = SQSFactory(endpoint_url="http://localstack:4566")

        assert isinstance(factory.create_producer(), SQSProducer)

    def test_create_consumer_returns_sqs_consumer(self) -> None:
        factory = SQSFactory(endpoint_url="http://localstack:4566")

        assert isinstance(factory.create_consumer(), SQSConsumer)

    def test_create_admin_returns_sqs_admin(self) -> None:
        factory = SQSFactory(endpoint_url="http://localstack:4566")

        assert isinstance(factory.create_admin(), SQSQueueAdmin)


class TestBuildBrokerFactory:
    @pytest.mark.parametrize(
        ("broker_name", "expected_type"),
        [
            ("rabbitmq", RabbitMQFactory),
            ("kafka", KafkaFactory),
            ("sqs", SQSFactory),
            ("RABBITMQ", RabbitMQFactory),
        ],
    )
    def test_returns_correct_factory_type(
        self, broker_name: str, expected_type: type
    ) -> None:
        factory = build_broker_factory(broker_name)

        assert isinstance(factory, expected_type)

    def test_unknown_broker_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="Unknown broker"):
            build_broker_factory("pulsar")
