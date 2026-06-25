"""Composition helpers for wiring the event store and publisher to real services."""

from __future__ import annotations

import os
from typing import cast

import psycopg2
from kafka import KafkaProducer

from event_sourcing.infrastructure.kafka_publisher import (
    KafkaEventPublisher,
    KafkaProducerLike,
)
from event_sourcing.infrastructure.postgres_event_store import (
    DBConnection,
    PostgresEventStore,
)


def build_connection() -> DBConnection:
    """Open a PostgreSQL connection from environment variables."""
    connection = psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", "5432")),
        dbname=os.environ.get("POSTGRES_DB", "event_sourcing"),
        user=os.environ.get("POSTGRES_USER", "postgres"),
        password=os.environ.get("POSTGRES_PASSWORD", "postgres"),
    )
    return cast(DBConnection, connection)


def build_event_store() -> PostgresEventStore:
    """Build the event store on top of a fresh PostgreSQL connection."""
    return PostgresEventStore(build_connection())


def build_producer() -> KafkaProducerLike:
    """Build a real KafkaProducer from environment variables."""
    bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    return cast(KafkaProducerLike, KafkaProducer(bootstrap_servers=bootstrap_servers))


def build_publisher() -> KafkaEventPublisher:
    """Build the event publisher on top of a real Kafka producer."""
    return KafkaEventPublisher(build_producer())
