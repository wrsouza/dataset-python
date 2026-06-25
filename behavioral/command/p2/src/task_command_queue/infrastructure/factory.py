"""Composition helpers for wiring the publisher to a real RabbitMQ broker."""

from __future__ import annotations

import os
from typing import cast

import pika

from task_command_queue.infrastructure.rabbitmq_publisher import (
    PikaChannel,
    RabbitMQTaskPublisher,
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


def build_publisher() -> RabbitMQTaskPublisher:
    """Build a RabbitMQTaskPublisher wired to a real RabbitMQ channel."""
    return RabbitMQTaskPublisher(build_channel())
