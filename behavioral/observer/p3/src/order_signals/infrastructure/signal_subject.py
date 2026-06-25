"""ConcreteSubject: dispatches OrderEvents through a real Django Signal.

`django.dispatch.Signal` is itself an Observer-pattern implementation —
`subscribe`/`unsubscribe`/`notify` here simply adapt our domain-level
`OrderObserver` ABC onto Django's `connect`/`disconnect`/`send` API, so
the rest of the codebase only ever depends on the domain abstraction.
"""

from __future__ import annotations

from typing import Any

from django.dispatch import Signal

from order_signals.domain.entities import OrderEvent
from order_signals.domain.interfaces import OrderObserver, OrderSubject

order_event_signal = Signal()


class DjangoSignalOrderSubject(OrderSubject):
    """Adapts our domain Subject/Observer ABCs onto a single Django Signal.

    Observers are meant to be subscribed once (e.g. at app startup, see
    `apps.py`), not per-request — `connect`/`disconnect` mutate Django's
    process-global signal dispatch table, so subscribing on every request
    would leak a duplicate receiver per request.
    """

    def __init__(self, signal: Signal | None = None) -> None:
        self._signal = signal if signal is not None else order_event_signal
        self._receivers: dict[int, Any] = {}

    def subscribe(self, observer: OrderObserver) -> None:
        def receiver(sender: object, event: OrderEvent, **kwargs: object) -> None:
            observer.on_order_event(event)

        self._receivers[id(observer)] = receiver
        self._signal.connect(receiver, weak=False)

    def unsubscribe(self, observer: OrderObserver) -> None:
        receiver = self._receivers.pop(id(observer), None)
        if receiver is not None:
            self._signal.disconnect(receiver)

    def notify(self, event: OrderEvent) -> None:
        self._signal.send(sender=self.__class__, event=event)
