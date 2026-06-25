"""Composition helpers for wiring the source to a real Kafka consumer."""

from __future__ import annotations

import json
import os
from typing import cast

from kafka import KafkaConsumer

from stream_iterator.infrastructure.kafka_source import (
    KafkaConsumerLike,
    KafkaMessageSource,
)


def build_consumer() -> KafkaConsumerLike:
    """Build a real KafkaConsumer for the configured topic."""
    topic = os.environ.get("KAFKA_TOPIC", "data-stream")
    bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        value_deserializer=lambda raw: json.loads(raw.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
    )
    return cast(KafkaConsumerLike, consumer)


def build_source() -> KafkaMessageSource:
    """Build the message source on top of a real Kafka consumer."""
    return KafkaMessageSource(build_consumer())
