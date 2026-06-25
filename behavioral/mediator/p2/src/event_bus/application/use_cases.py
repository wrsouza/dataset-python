"""Use cases orchestrating subscription and event publishing through the bus."""

from __future__ import annotations

from event_bus.domain.entities import Event
from event_bus.domain.interfaces import EventBus, EventHandler


class SubscribeUseCase:
    """Registers a handler with the bus for a given event type."""

    def __init__(self, bus: EventBus) -> None:
        self._bus = bus

    def execute(self, event_type: str, handler: EventHandler) -> None:
        self._bus.subscribe(event_type, handler)


class PublishEventUseCase:
    """Publishes an event through the bus, on behalf of a caller."""

    def __init__(self, bus: EventBus) -> None:
        self._bus = bus

    def execute(self, event_type: str, payload: dict[str, object]) -> Event:
        return self._bus.publish(event_type, payload)
