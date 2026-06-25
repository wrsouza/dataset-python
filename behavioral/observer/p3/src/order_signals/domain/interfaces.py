"""Observer pattern interfaces for the Order domain.

Defines the Subject (OrderSubject) and Observer (OrderObserver) ABCs.
Concrete subjects decide HOW to distribute events (in-memory, a Django
signal, etc.) while this interface stays stable.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from order_signals.domain.entities import OrderEvent


class OrderObserver(ABC):
    """Abstract base for all order event observers.

    OCP: new observer types extend this without modifying OrderSubject.
    DIP: OrderSubject depends on this abstraction, not concrete classes.
    """

    @abstractmethod
    def on_order_event(self, event: OrderEvent) -> None:
        """React to an order being created or changing status."""
        ...


class OrderSubject(ABC):
    """Subject ABC — maintains observer list and drives notifications."""

    @abstractmethod
    def subscribe(self, observer: OrderObserver) -> None:
        """Register an observer to receive every future order event."""
        ...

    @abstractmethod
    def unsubscribe(self, observer: OrderObserver) -> None:
        """Remove a previously registered observer."""
        ...

    @abstractmethod
    def notify(self, event: OrderEvent) -> None:
        """Broadcast an order event to every subscribed observer."""
        ...
