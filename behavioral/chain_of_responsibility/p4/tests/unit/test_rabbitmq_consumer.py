"""Unit tests for RabbitMQQueueConsumer using a fake pika channel."""

from __future__ import annotations

import json
from dataclasses import dataclass

from message_pipeline.domain.entities import IncomingMessage
from message_pipeline.infrastructure.rabbitmq_consumer import RabbitMQQueueConsumer


@dataclass
class FakeMethod:
    delivery_tag: int


class FakeChannel:
    def __init__(self, messages: list[dict[str, object]]) -> None:
        self._messages = messages
        self._next_tag = 1
        self.declared_queues: list[str] = []
        self.acked_tags: list[int] = []

    def queue_declare(self, queue: str, durable: bool = True) -> None:
        self.declared_queues.append(queue)

    def basic_get(
        self, queue: str, auto_ack: bool = False
    ) -> tuple[FakeMethod | None, object, bytes | None]:
        if not self._messages:
            return None, None, None
        payload = self._messages.pop(0)
        method = FakeMethod(delivery_tag=self._next_tag)
        self._next_tag += 1
        return method, None, json.dumps(payload).encode("utf-8")

    def basic_ack(self, delivery_tag: int) -> None:
        self.acked_tags.append(delivery_tag)


def test_consume_yields_messages_up_to_limit() -> None:
    channel = FakeChannel(
        [
            {"message_id": "m-1", "order_id": "o-1", "amount": 10},
            {"message_id": "m-2", "order_id": "o-2", "amount": 20},
        ]
    )
    consumer = RabbitMQQueueConsumer(channel)

    messages = list(consumer.consume("orders", limit=5))

    assert [m.message_id for m in messages] == ["m-1", "m-2"]
    assert channel.declared_queues == ["orders"]


def test_consume_stops_at_limit_even_if_more_messages_available() -> None:
    channel = FakeChannel(
        [
            {"message_id": "m-1", "order_id": "o-1", "amount": 10},
            {"message_id": "m-2", "order_id": "o-2", "amount": 20},
        ]
    )
    consumer = RabbitMQQueueConsumer(channel)

    messages = list(consumer.consume("orders", limit=1))

    assert [m.message_id for m in messages] == ["m-1"]


def test_ack_calls_basic_ack_with_correct_delivery_tag() -> None:
    channel = FakeChannel([{"message_id": "m-1", "order_id": "o-1", "amount": 10}])
    consumer = RabbitMQQueueConsumer(channel)

    [message] = list(consumer.consume("orders", limit=1))
    consumer.ack(message)

    assert channel.acked_tags == [1]


def test_ack_is_noop_for_unknown_message() -> None:
    channel = FakeChannel([])
    consumer = RabbitMQQueueConsumer(channel)

    consumer.ack(IncomingMessage(message_id="unknown", payload={}))

    assert channel.acked_tags == []


def test_falls_back_to_order_id_when_message_id_missing() -> None:
    channel = FakeChannel([{"order_id": "o-99", "amount": 5}])
    consumer = RabbitMQQueueConsumer(channel)

    [message] = list(consumer.consume("orders", limit=1))

    assert message.message_id == "o-99"
