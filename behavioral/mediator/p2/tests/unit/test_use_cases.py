"""Unit tests for SubscribeUseCase and PublishEventUseCase."""

from __future__ import annotations

from event_bus.application.use_cases import PublishEventUseCase, SubscribeUseCase
from event_bus.infrastructure.handlers import LoggingEventHandler
from event_bus.infrastructure.rabbitmq_event_bus import RabbitMQEventBus
from tests.unit.test_rabbitmq_event_bus import FakeChannel


def test_subscribe_then_publish_delivers_event_to_handler() -> None:
    bus = RabbitMQEventBus(FakeChannel())
    handler = LoggingEventHandler()
    SubscribeUseCase(bus).execute("order.created", handler)

    event = PublishEventUseCase(bus).execute("order.created", {"order_id": "o-1"})

    assert handler.received == [event]


def test_publish_returns_the_event_it_created() -> None:
    bus = RabbitMQEventBus(FakeChannel())

    event = PublishEventUseCase(bus).execute("order.created", {"order_id": "o-1"})

    assert event.event_type == "order.created"
    assert event.payload == {"order_id": "o-1"}
