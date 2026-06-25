"""Unit tests for DjangoSignalOrderSubject.

Each test builds the subject with its own fresh `Signal()` instance so
that receivers connected in one test never leak into another — the
real `order_event_signal` is shared process-wide and is only ever
subscribed to once, at module import time (see `django_app/views.py`).
"""

from __future__ import annotations

from django.dispatch import Signal

from order_signals.domain.entities import OrderEvent
from order_signals.domain.interfaces import OrderObserver
from order_signals.infrastructure.signal_subject import DjangoSignalOrderSubject


class RecordingObserver(OrderObserver):
    def __init__(self) -> None:
        self.events: list[OrderEvent] = []

    def on_order_event(self, event: OrderEvent) -> None:
        self.events.append(event)


def test_subscribed_observer_receives_notification() -> None:
    subject = DjangoSignalOrderSubject(Signal())
    observer = RecordingObserver()
    subject.subscribe(observer)

    event = OrderEvent(order_id="o1", status="created", total=10.0)
    subject.notify(event)

    assert observer.events == [event]


def test_multiple_observers_all_receive_the_same_event() -> None:
    subject = DjangoSignalOrderSubject(Signal())
    first = RecordingObserver()
    second = RecordingObserver()
    subject.subscribe(first)
    subject.subscribe(second)

    event = OrderEvent(order_id="o1", status="created", total=10.0)
    subject.notify(event)

    assert first.events == [event]
    assert second.events == [event]


def test_unsubscribed_observer_stops_receiving_events() -> None:
    subject = DjangoSignalOrderSubject(Signal())
    observer = RecordingObserver()
    subject.subscribe(observer)
    subject.unsubscribe(observer)

    subject.notify(OrderEvent(order_id="o1", status="created", total=10.0))

    assert observer.events == []


def test_unsubscribe_unknown_observer_is_a_no_op() -> None:
    subject = DjangoSignalOrderSubject(Signal())
    observer = RecordingObserver()

    subject.unsubscribe(observer)  # should not raise
