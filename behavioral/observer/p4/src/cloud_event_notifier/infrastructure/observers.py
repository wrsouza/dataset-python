"""ConcreteObservers reacting to locally published CloudEvents.

OCP: a new local reaction is added by writing a new class implementing
CloudEventObserver and subscribing it, without touching SnsCloudEventPublisher.
"""

from __future__ import annotations

from collections.abc import Callable

from cloud_event_notifier.domain.entities import CloudEvent
from cloud_event_notifier.domain.interfaces import CloudEventObserver


class ConsoleObserver(CloudEventObserver):
    """Writes a human-readable line for every event, via an injected
    writer (defaults to `print`) so the CLI can pass `typer.echo`."""

    def __init__(self, writer: Callable[[str], None] = print) -> None:
        self._writer = writer

    def on_cloud_event(self, event: CloudEvent) -> None:
        self._writer(f"[{event.event_type}] {event.payload} (id={event.event_id})")


class EventLogObserver(CloudEventObserver):
    """Keeps every published event in memory — useful for tests and for
    any caller that wants to inspect what was fanned out locally."""

    def __init__(self) -> None:
        self.events: list[CloudEvent] = []

    def on_cloud_event(self, event: CloudEvent) -> None:
        self.events.append(event)
