"""RabbitMQ-backed implementation of EventBus.

Dispatch to locally registered handlers is synchronous and immediate —
the Mediator's core job. Publishing to a RabbitMQ fanout exchange runs
alongside it, so every other server process bound to the same exchange
can pick up the event too (consuming that fan-out is a separate
concern, outside this single-process demo).

Handlers may subscribe to a specific `event_type`, or to `"*"` to
receive every event regardless of type.
"""

from __future__ import annotations

import json
from typing import Protocol

from event_bus.domain.entities import Event
from event_bus.domain.interfaces import EventBus, EventHandler

WILDCARD_EVENT_TYPE = "*"


class PikaChannel(Protocol):
    """Minimal pika channel contract this bus relies on."""

    def exchange_declare(self, exchange: str, exchange_type: str) -> object: ...

    def basic_publish(self, exchange: str, routing_key: str, body: bytes) -> None: ...


class RabbitMQEventBus(EventBus):
    """Routes events to local handlers and fans them out via a RabbitMQ exchange."""

    def __init__(self, channel: PikaChannel, exchange: str = "events") -> None:
        self._channel = channel
        self._exchange = exchange
        self._handlers: dict[str, list[EventHandler]] = {}
        self._channel.exchange_declare(exchange=exchange, exchange_type="fanout")

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        handlers = self._handlers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)

    def publish(self, event_type: str, payload: dict[str, object]) -> Event:
        event = Event(event_type=event_type, payload=payload)

        self._channel.basic_publish(
            exchange=self._exchange, routing_key="", body=self._serialize(event)
        )
        recipients = [
            *self._handlers.get(event_type, []),
            *self._handlers.get(WILDCARD_EVENT_TYPE, []),
        ]
        for handler in recipients:
            handler.handle(event)

        return event

    @staticmethod
    def _serialize(event: Event) -> bytes:
        return json.dumps(
            {
                "event_type": event.event_type,
                "payload": event.payload,
                "published_at": event.published_at.isoformat(),
            }
        ).encode("utf-8")
