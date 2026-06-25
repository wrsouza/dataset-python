"""Shared pytest fixtures for P5 — Messaging Protocol Adapter."""

from __future__ import annotations

import pytest

from messaging_adapter.domain.entities import BrokerType, ConsumeConfig, PublishConfig
from messaging_adapter.infrastructure.kafka_adapter import KafkaAdapter
from messaging_adapter.infrastructure.rabbitmq_adapter import RabbitMQAdapter


@pytest.fixture
def rabbitmq_adapter() -> RabbitMQAdapter:
    return RabbitMQAdapter()


@pytest.fixture
def kafka_adapter() -> KafkaAdapter:
    return KafkaAdapter()


@pytest.fixture
def rabbitmq_publish_config() -> PublishConfig:
    return PublishConfig(broker=BrokerType.RABBITMQ, topic="payments")


@pytest.fixture
def kafka_publish_config() -> PublishConfig:
    return PublishConfig(broker=BrokerType.KAFKA, topic="orders")


@pytest.fixture
def rabbitmq_consume_config() -> ConsumeConfig:
    return ConsumeConfig(broker=BrokerType.RABBITMQ, topic="payments", limit=3)


@pytest.fixture
def kafka_consume_config() -> ConsumeConfig:
    return ConsumeConfig(broker=BrokerType.KAFKA, topic="orders", limit=3)
