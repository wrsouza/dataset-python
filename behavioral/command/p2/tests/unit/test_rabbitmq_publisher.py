"""Unit tests for RabbitMQTaskPublisher using a fake pika channel."""

from __future__ import annotations

import json

from task_command_queue.infrastructure.rabbitmq_publisher import RabbitMQTaskPublisher


class FakeChannel:
    def __init__(self) -> None:
        self.declared_queues: list[str] = []
        self.published: list[tuple[str, str, bytes]] = []

    def queue_declare(self, queue: str, durable: bool = True) -> None:
        self.declared_queues.append(queue)

    def basic_publish(self, exchange: str, routing_key: str, body: bytes) -> None:
        self.published.append((exchange, routing_key, body))


def test_publisher_declares_queue_on_construction() -> None:
    channel = FakeChannel()

    RabbitMQTaskPublisher(channel, queue="my_queue")

    assert channel.declared_queues == ["my_queue"]


def test_publish_sends_serialised_command_to_default_queue() -> None:
    channel = FakeChannel()
    publisher = RabbitMQTaskPublisher(channel)

    publisher.publish("send_email", {"to": "a@b.com"})

    [(exchange, routing_key, body)] = channel.published
    assert exchange == ""
    assert routing_key == "task_queue"
    assert json.loads(body) == {
        "command_name": "send_email",
        "payload": {"to": "a@b.com"},
    }
