"""Observer pattern interfaces for the Stock Ticker domain.

Defines the Subject (StockMarket) and Observer (StockObserver) ABCs
that form the core of the Observer pattern implementation.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from stock_ticker.domain.entities import StockEvent


class StockObserver(ABC):
    """Abstract base for all stock market observers.

    OCP: new observer types extend this without modifying StockMarket.
    DIP: StockMarket depends on this abstraction, not concrete classes.
    """

    @abstractmethod
    async def update(self, event: StockEvent) -> None:
        """Receive a stock price update event."""
        ...


class StockMarket(ABC):
    """Subject ABC — maintains observer list and drives notifications.

    Concrete implementations decide HOW to distribute events
    (in-process, Redis PubSub, etc.) while the interface stays stable.
    """

    @abstractmethod
    def subscribe(
        self,
        observer: StockObserver,
        tickers: list[str],
    ) -> None:
        """Register an observer for a set of ticker symbols."""
        ...

    @abstractmethod
    def unsubscribe(self, observer: StockObserver) -> None:
        """Remove an observer from all subscriptions."""
        ...

    @abstractmethod
    async def notify(
        self,
        ticker: str,
        price: float,
        change_pct: float,
    ) -> None:
        """Notify all observers subscribed to *ticker*."""
        ...
