"""Composition helpers for wiring the consumer to a real RabbitMQ broker."""

from __future__ import annotations

import os
from typing import cast

import pika

from message_pipeline.infrastructure.rabbitmq_consumer import (
    PikaChannel,
    RabbitMQQueueConsumer,
)


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


def build_consumer() -> RabbitMQQueueConsumer:
    """Build a RabbitMQQueueConsumer wired to a real RabbitMQ channel."""
    return RabbitMQQueueConsumer(build_channel())
