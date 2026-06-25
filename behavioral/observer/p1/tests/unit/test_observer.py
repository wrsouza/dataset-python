"""Unit tests for Observer pattern — P1 Stock Ticker."""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock

import pytest

from stock_ticker.domain.entities import AlertRule, StockEvent
from stock_ticker.infrastructure.observers import (
    AlertObserver,
    LoggingObserver,
    WebSocketObserver,
)
from stock_ticker.infrastructure.redis_subject import RedisStockMarket


# ── Minimal in-memory market for unit tests (no Redis needed) ────────────────

class InMemoryStockMarket:
    """Test double: in-process market without Redis."""

    def __init__(self) -> None:
        from collections import defaultdict
        self._subscriptions: dict[str, list] = defaultdict(list)

    def subscribe(self, observer: object, tickers: list[str]) -> None:
        for ticker in tickers:
            if observer not in self._subscriptions[ticker]:
                self._subscriptions[ticker].append(observer)

    def unsubscribe(self, observer: object) -> None:
        for observers in self._subscriptions.values():
            if observer in observers:
                observers.remove(observer)

    async def notify(self, ticker: str, price: float, change_pct: float) -> None:
        event = StockEvent(ticker=ticker, price=price, change_pct=change_pct)
        for observer in list(self._subscriptions.get(ticker, [])):
            await observer.update(event)


# ── Tests ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_subscribe_then_notify_calls_observer() -> None:
    """Core Observer contract: subscribed observer receives the event."""
    market = InMemoryStockMarket()
    observer = AsyncMock()
    observer.update = AsyncMock()

    market.subscribe(observer, ["AAPL"])
    await market.notify("AAPL", price=150.0, change_pct=1.5)

    observer.update.assert_called_once()
    event: StockEvent = observer.update.call_args[0][0]
    assert event.ticker == "AAPL"
    assert event.price == 150.0


@pytest.mark.asyncio
async def test_unsubscribe_stops_notifications() -> None:
    """Core Observer contract: unsubscribed observer receives nothing."""
    market = InMemoryStockMarket()
    observer = AsyncMock()
    observer.update = AsyncMock()

    market.subscribe(observer, ["MSFT"])
    market.unsubscribe(observer)
    await market.notify("MSFT", price=300.0, change_pct=-0.5)

    observer.update.assert_not_called()


@pytest.mark.asyncio
async def test_multiple_observers_all_notified() -> None:
    """Multiple observers subscribed to the same ticker all receive the event."""
    market = InMemoryStockMarket()
    obs1 = AsyncMock()
    obs1.update = AsyncMock()
    obs2 = AsyncMock()
    obs2.update = AsyncMock()

    market.subscribe(obs1, ["GOOG"])
    market.subscribe(obs2, ["GOOG"])
    await market.notify("GOOG", price=2800.0, change_pct=0.3)

    obs1.update.assert_called_once()
    obs2.update.assert_called_once()


@pytest.mark.asyncio
async def test_observer_only_receives_subscribed_tickers() -> None:
    """Observer subscribed to AAPL should not receive MSFT events."""
    market = InMemoryStockMarket()
    observer = AsyncMock()
    observer.update = AsyncMock()

    market.subscribe(observer, ["AAPL"])
    await market.notify("MSFT", price=300.0, change_pct=2.0)

    observer.update.assert_not_called()


@pytest.mark.asyncio
async def test_alert_observer_fires_above_threshold() -> None:
    rule = AlertRule(alert_id="a1", ticker="TSLA", threshold_pct=2.0)
    alert_obs = AlertObserver(rules=[rule])

    event = StockEvent(ticker="TSLA", price=900.0, change_pct=3.5)
    await alert_obs.update(event)

    assert len(alert_obs.triggered_alerts) == 1
    assert alert_obs.triggered_alerts[0]["alert_id"] == "a1"


@pytest.mark.asyncio
async def test_alert_observer_silent_below_threshold() -> None:
    rule = AlertRule(alert_id="a2", ticker="TSLA", threshold_pct=5.0)
    alert_obs = AlertObserver(rules=[rule])

    event = StockEvent(ticker="TSLA", price=900.0, change_pct=1.0)
    await alert_obs.update(event)

    assert len(alert_obs.triggered_alerts) == 0


@pytest.mark.asyncio
async def test_logging_observer_increments_tick_count() -> None:
    log_obs = LoggingObserver()
    event = StockEvent(ticker="AMZN", price=3200.0, change_pct=-0.8)

    await log_obs.update(event)
    await log_obs.update(event)

    assert log_obs.tick_count == 2


def test_stock_event_significant_move() -> None:
    event = StockEvent(ticker="META", price=350.0, change_pct=4.0)
    assert event.is_significant_move(threshold_pct=3.0) is True
    assert event.is_significant_move(threshold_pct=5.0) is False


def test_redis_market_subscribe_unsubscribe() -> None:
    """Unit: verify subscription registry without connecting to Redis."""
    market = RedisStockMarket(redis_url="redis://fake:6379")
    obs = AsyncMock()

    market.subscribe(obs, ["AAPL", "MSFT"])
    assert obs in market._subscriptions["AAPL"]
    assert obs in market._subscriptions["MSFT"]

    market.unsubscribe(obs)
    assert obs not in market._subscriptions["AAPL"]
    assert obs not in market._subscriptions["MSFT"]
