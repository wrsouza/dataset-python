"""Composition helpers for wiring the event bus to a real RabbitMQ broker."""

from __future__ import annotations

import os
from typing import cast

import pika

from event_bus.infrastructure.rabbitmq_event_bus import PikaChannel, RabbitMQEventBus


def build_channel() -> PikaChannel:
    """Open a blocking connection to RabbitMQ and return its channel."""
    credentials = pika.PlainCredentials(
        os.environ.get("RABBITMQ_USER", "guest"),
        os.environ.get("RABBITMQ_PASSWORD", "guest"),
    )
    parameters = pika.ConnectionParameters(
        host=os.environ.get("RABBITMQ_HOST", "localhost"),
        port=int(os.environ.get("RABBITMQ_PORT", "5672")),
        credentials=credentials,
    )
    connection = pika.BlockingConnection(parameters)
    return cast(PikaChannel, connection.channel())


def build_event_bus() -> RabbitMQEventBus:
    """Build the event bus wired to a real RabbitMQ channel."""
    return RabbitMQEventBus(build_channel())
