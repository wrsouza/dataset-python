"""Shared pytest fixtures for P4 — Message Consumer Factory."""
from __future__ import annotations

import pytest

from messaging.domain.entities import BrokerType, ConsumeConfig


@pytest.fixture
def kafka_config() -> ConsumeConfig:
    return ConsumeConfig(
        broker=BrokerType.KAFKA,
        topic_or_queue="orders",
        group_id="test-group",
        limit=3,
    )


@pytest.fixture
def rabbitmq_config() -> ConsumeConfig:
    return ConsumeConfig(
        broker=BrokerType.RABBITMQ,
        topic_or_queue="payments",
        group_id="test-group",
        limit=3,
    )


@pytest.fixture
def sqs_config() -> ConsumeConfig:
    return ConsumeConfig(
        broker=BrokerType.SQS,
        topic_or_queue="notifications",
        group_id="test-group",
        limit=3,
    )
