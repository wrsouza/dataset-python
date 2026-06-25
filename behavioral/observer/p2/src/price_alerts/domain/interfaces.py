"""Observer pattern interfaces for the Price Alerts domain."""

from __future__ import annotations

from abc import ABC, abstractmethod

from price_alerts.domain.entities import PriceEvent, Subscription


class PriceObserver(ABC):
    """Abstract observer for price-change notifications.

    OCP: new notification channels extend this without modifying PriceMonitor.
    DIP: PriceMonitor depends on this abstraction.
    """

    @abstractmethod
    def on_price_change(self, event: PriceEvent) -> None:
        """Handle a price-change event."""
        ...

    @property
    @abstractmethod
    def observer_id(self) -> str:
        """Unique identifier for this observer instance."""
        ...


class PriceMonitor(ABC):
    """Subject ABC — orchestrates observer subscriptions and notifications."""

    @abstractmethod
    def subscribe(
        self,
        observer: PriceObserver,
        product_id: str,
        threshold: float,
    ) -> str:
        """Register observer for a product; return subscription_id."""
        ...

    @abstractmethod
    def unsubscribe(self, subscription_id: str) -> None:
        """Remove a subscription by ID."""
        ...

    @abstractmethod
    def notify_price_change(
        self,
        product_id: str,
        old_price: float,
        new_price: float,
    ) -> None:
        """Broadcast a price change to all matching observers."""
        ...

    @property
    @abstractmethod
    def subscriptions(self) -> dict[str, Subscription]:
        """Return a snapshot of all current subscriptions."""
        ...
