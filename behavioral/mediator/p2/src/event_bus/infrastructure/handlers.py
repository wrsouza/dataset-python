"""Example EventHandlers used by the demo Flask app."""

from __future__ import annotations

from event_bus.domain.entities import Event
from event_bus.domain.interfaces import EventHandler


class LoggingEventHandler(EventHandler):
    """Records every event it receives, in memory, for inspection via the API."""

    def __init__(self, handler_id: str = "logging-handler") -> None:
        self._handler_id = handler_id
        self.received: list[Event] = []

    def get_handler_id(self) -> str:
        return self._handler_id

    def handle(self, event: Event) -> None:
        self.received.append(event)
