"""RabbitMQ-backed implementation of TaskPublisher, built on pika."""

from __future__ import annotations

import json
from typing import Protocol

from task_command_queue.domain.interfaces import TaskPublisher


class PikaChannel(Protocol):
    """Minimal pika channel contract this publisher relies on."""

    def queue_declare(self, queue: str, durable: bool = True) -> object: ...

    def basic_publish(self, exchange: str, routing_key: str, body: bytes) -> None: ...


class RabbitMQTaskPublisher(TaskPublisher):
    """Publishes each executed command's name and payload for audit/replay."""

    def __init__(self, channel: PikaChannel, queue: str = "task_queue") -> None:
        self._channel = channel
        self._queue = queue
        self._channel.queue_declare(queue=queue, durable=True)

    def publish(self, command_name: str, payload: dict[str, object]) -> None:
        body = json.dumps({"command_name": command_name, "payload": payload})
        self._channel.basic_publish(
            exchange="", routing_key=self._queue, body=body.encode("utf-8")
        )
