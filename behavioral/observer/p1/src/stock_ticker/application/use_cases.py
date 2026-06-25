"""Application-layer use cases for the Stock Ticker.

Use cases depend only on domain abstractions (DIP).
"""
from __future__ import annotations

import uuid

from stock_ticker.domain.entities import AlertRule
from stock_ticker.domain.interfaces import StockMarket, StockObserver


class SubscribeToTickersUseCase:
    """Register an observer to receive updates for specified tickers."""

    def __init__(self, market: StockMarket) -> None:
        self._market = market

    def execute(self, observer: StockObserver, tickers: list[str]) -> None:
        if not tickers:
            raise ValueError("At least one ticker must be specified")
        self._market.subscribe(observer, tickers)


class UnsubscribeObserverUseCase:
    """Remove an observer from all ticker subscriptions."""

    def __init__(self, market: StockMarket) -> None:
        self._market = market

    def execute(self, observer: StockObserver) -> None:
        self._market.unsubscribe(observer)


class CreateAlertRuleUseCase:
    """Factory: create a validated AlertRule with a unique ID."""

    def execute(
        self,
        ticker: str,
        threshold_pct: float,
        webhook_url: str | None = None,
    ) -> AlertRule:
        if threshold_pct <= 0:
            raise ValueError("threshold_pct must be positive")
        return AlertRule(
            alert_id=str(uuid.uuid4()),
            ticker=ticker.upper(),
            threshold_pct=threshold_pct,
            webhook_url=webhook_url,
        )
