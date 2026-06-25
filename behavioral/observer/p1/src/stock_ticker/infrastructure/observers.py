"""ConcreteObservers for the Stock Ticker domain.

Each observer has exactly one responsibility (SRP):
- WebSocketObserver  → push events to a WebSocket client
- AlertObserver      → fire when price move exceeds threshold
- LoggingObserver    → record every tick to application logs
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from stock_ticker.domain.entities import AlertRule, StockEvent
from stock_ticker.domain.interfaces import StockObserver

if TYPE_CHECKING:
    from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketObserver(StockObserver):
    """Pushes StockEvents to a connected WebSocket client (OCP-compliant)."""

    def __init__(self, websocket: "WebSocket", client_id: str) -> None:
        self._ws = websocket
        self._client_id = client_id

    async def update(self, event: StockEvent) -> None:
        payload = {
            "ticker": event.ticker,
            "price": event.price,
            "change_pct": event.change_pct,
            "timestamp": event.timestamp.isoformat(),
        }
        try:
            await self._ws.send_json(payload)
        except Exception:
            logger.warning("WebSocket %s disconnected", self._client_id)

    def __repr__(self) -> str:
        return f"WebSocketObserver(client={self._client_id})"


class AlertObserver(StockObserver):
    """Fires an alert when a price move exceeds a configured threshold.

    Demonstrates OCP: new alert rules are injected without changing this class.
    """

    def __init__(self, rules: list[AlertRule]) -> None:
        self._rules = rules
        self._triggered: list[dict[str, object]] = []

    async def update(self, event: StockEvent) -> None:
        for rule in self._rules:
            if rule.ticker != event.ticker:
                continue
            if event.is_significant_move(rule.threshold_pct):
                alert = {
                    "alert_id": rule.alert_id,
                    "ticker": event.ticker,
                    "price": event.price,
                    "change_pct": event.change_pct,
                    "threshold_pct": rule.threshold_pct,
                    "timestamp": event.timestamp.isoformat(),
                }
                self._triggered.append(alert)
                logger.warning(
                    "ALERT %s: %s moved %.2f%% (threshold %.1f%%)",
                    rule.alert_id,
                    event.ticker,
                    event.change_pct,
                    rule.threshold_pct,
                )

    @property
    def triggered_alerts(self) -> list[dict[str, object]]:
        return list(self._triggered)

    def __repr__(self) -> str:
        return f"AlertObserver(rules={len(self._rules)})"


class LoggingObserver(StockObserver):
    """Records every tick to the application log (single responsibility)."""

    def __init__(self, log_level: int = logging.INFO) -> None:
        self._log_level = log_level
        self._tick_count = 0

    async def update(self, event: StockEvent) -> None:
        self._tick_count += 1
        logger.log(
            self._log_level,
            "[%d] %s @ $%.2f (%+.2f%%)",
            self._tick_count,
            event.ticker,
            event.price,
            event.change_pct,
        )

    @property
    def tick_count(self) -> int:
        return self._tick_count

    def __repr__(self) -> str:
        return f"LoggingObserver(ticks={self._tick_count})"
