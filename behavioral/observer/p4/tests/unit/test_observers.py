"""Unit tests for ConsoleObserver and EventLogObserver."""

from __future__ import annotations

from cloud_event_notifier.domain.entities import CloudEvent
from cloud_event_notifier.infrastructure.observers import (
    ConsoleObserver,
    EventLogObserver,
)


def test_console_observer_writes_formatted_line() -> None:
    lines: list[str] = []
    observer = ConsoleObserver(writer=lines.append)
    event = CloudEvent(event_type="order.created", payload={"order_id": "o1"})

    observer.on_cloud_event(event)

    assert len(lines) == 1
    assert "order.created" in lines[0]
    assert "o1" in lines[0]


def test_event_log_observer_records_every_event() -> None:
    observer = EventLogObserver()
    first = CloudEvent(event_type="order.created", payload={})
    second = CloudEvent(event_type="order.shipped", payload={})

    observer.on_cloud_event(first)
    observer.on_cloud_event(second)

    assert observer.events == [first, second]
