"""RabbitMQ-backed implementation of QueueConsumer, built on pika."""

from __future__ import annotations

import json
from collections.abc import Iterator
from typing import Protocol

from message_pipeline.domain.entities import IncomingMessage
from message_pipeline.domain.interfaces import QueueConsumer


class BasicGetMethod(Protocol):
    """Shape of the `method` frame returned by pika's `basic_get`."""

    delivery_tag: int


class PikaChannel(Protocol):
    """Minimal pika channel contract this consumer relies on."""

    def queue_declare(self, queue: str, durable: bool = True) -> object: ...

    def basic_get(
        self, queue: str, auto_ack: bool = False
    ) -> tuple[BasicGetMethod | None, object, bytes | None]: ...

    def basic_ack(self, delivery_tag: int) -> None: ...


class RabbitMQQueueConsumer(QueueConsumer):
    """Pulls messages from a RabbitMQ queue via `basic_get` polling."""

    def __init__(self, channel: PikaChannel) -> None:
        self._channel = channel
        self._delivery_tags: dict[str, int] = {}

    def consume(self, queue: str, limit: int) -> Iterator[IncomingMessage]:
        self._channel.queue_declare(queue=queue, durable=True)
        delivered = 0
        while delivered < limit:
            method, _properties, body = self._channel.basic_get(
                queue=queue, auto_ack=False
            )
            if method is None or body is None:
                return
            message = self._to_incoming_message(body)
            self._delivery_tags[message.message_id] = method.delivery_tag
            delivered += 1
            yield message

    def ack(self, message: IncomingMessage) -> None:
        delivery_tag = self._delivery_tags.pop(message.message_id, None)
        if delivery_tag is not None:
            self._channel.basic_ack(delivery_tag=delivery_tag)

    @staticmethod
    def _to_incoming_message(body: bytes) -> IncomingMessage:
        payload = json.loads(body.decode("utf-8"))
        message_id = str(payload.get("message_id", payload.get("order_id", "")))
        return IncomingMessage(message_id=message_id, payload=payload)
