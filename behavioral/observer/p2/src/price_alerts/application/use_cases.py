"""Application-layer use cases for the Price Alerts domain.

Use cases depend only on domain abstractions (DIP): they receive a
PriceMonitor (Subject) and PriceObserver instances via constructor/method
injection, never instantiating concrete infrastructure themselves.
"""

from __future__ import annotations

from price_alerts.domain.entities import Subscription
from price_alerts.domain.interfaces import PriceMonitor, PriceObserver

MIN_THRESHOLD_PCT = 0.0


class RegisterPriceAlertUseCase:
    """Subscribe an observer to price changes of a product."""

    def __init__(self, monitor: PriceMonitor) -> None:
        self._monitor = monitor

    def execute(
        self,
        observer: PriceObserver,
        product_id: str,
        threshold: float,
    ) -> str:
        if not product_id:
            raise ValueError("product_id must not be empty")
        if threshold <= MIN_THRESHOLD_PCT:
            raise ValueError("threshold must be a positive percentage")
        return self._monitor.subscribe(observer, product_id, threshold)


class RemovePriceAlertUseCase:
    """Unsubscribe a previously registered alert by its subscription id."""

    def __init__(self, monitor: PriceMonitor) -> None:
        self._monitor = monitor

    def execute(self, subscription_id: str) -> None:
        self._monitor.unsubscribe(subscription_id)


class ListPriceAlertsUseCase:
    """Return all currently registered subscriptions."""

    def __init__(self, monitor: PriceMonitor) -> None:
        self._monitor = monitor

    def execute(self) -> list[Subscription]:
        return list(self._monitor.subscriptions.values())


class ProcessPriceUpdateUseCase:
    """Process an incoming price update and notify matching observers.

    This is the entry point used by the Kafka consumer/worker: it delegates
    the actual fan-out logic to the Subject (PriceMonitor), keeping the
    use case itself framework- and broker-agnostic.
    """

    def __init__(self, monitor: PriceMonitor) -> None:
        self._monitor = monitor

    def execute(self, product_id: str, old_price: float, new_price: float) -> None:
        self._monitor.notify_price_change(product_id, old_price, new_price)
