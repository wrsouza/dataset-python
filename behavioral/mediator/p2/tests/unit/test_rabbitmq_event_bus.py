"""Unit tests for RabbitMQEventBus using a fake pika channel."""

from __future__ import annotations

from event_bus.domain.entities import Event
from event_bus.domain.interfaces import EventHandler
from event_bus.infrastructure.rabbitmq_event_bus import RabbitMQEventBus


class FakeChannel:
    def __init__(self) -> None:
        self.declared_exchanges: list[tuple[str, str]] = []
        self.published: list[tuple[str, str, bytes]] = []

    def exchange_declare(self, exchange: str, exchange_type: str) -> None:
        self.declared_exchanges.append((exchange, exchange_type))

    def basic_publish(self, exchange: str, routing_key: str, body: bytes) -> None:
        self.published.append((exchange, routing_key, body))


class RecordingHandler(EventHandler):
    def __init__(self, handler_id: str) -> None:
        self._handler_id = handler_id
        self.received: list[Event] = []

    def get_handler_id(self) -> str:
        return self._handler_id

    def handle(self, event: Event) -> None:
        self.received.append(event)


def test_constructor_declares_fanout_exchange() -> None:
    channel = FakeChannel()

    RabbitMQEventBus(channel, exchange="my-events")

    assert channel.declared_exchanges == [("my-events", "fanout")]


def test_publish_dispatches_to_subscribed_handler() -> None:
    bus = RabbitMQEventBus(FakeChannel())
    handler = RecordingHandler("h1")
    bus.subscribe("order.created", handler)

    event = bus.publish("order.created", {"order_id": "o-1"})

    assert handler.received == [event]


def test_publish_does_not_dispatch_to_handler_of_a_different_type() -> None:
    bus = RabbitMQEventBus(FakeChannel())
    handler = RecordingHandler("h1")
    bus.subscribe("order.created", handler)

    bus.publish("order.cancelled", {"order_id": "o-1"})

    assert handler.received == []


def test_publish_dispatches_to_wildcard_subscriber() -> None:
    bus = RabbitMQEventBus(FakeChannel())
    handler = RecordingHandler("audit")
    bus.subscribe("*", handler)

    bus.publish("order.created", {})
    bus.publish("order.cancelled", {})

    assert len(handler.received) == 2


def test_unsubscribe_stops_future_dispatch() -> None:
    bus = RabbitMQEventBus(FakeChannel())
    handler = RecordingHandler("h1")
    bus.subscribe("order.created", handler)
    bus.unsubscribe("order.created", handler)

    bus.publish("order.created", {})

    assert handler.received == []


def test_publish_also_publishes_to_rabbitmq_exchange() -> None:
    channel = FakeChannel()
    bus = RabbitMQEventBus(channel, exchange="my-events")

    bus.publish("order.created", {"order_id": "o-1"})

    [(exchange, routing_key, body)] = channel.published
    assert exchange == "my-events"
    assert routing_key == ""
    assert b"order.created" in body
