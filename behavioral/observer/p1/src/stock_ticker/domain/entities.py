"""Domain entities for the Stock Ticker domain."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class StockEvent:
    """Immutable value object representing a stock price update."""

    ticker: str
    price: float
    change_pct: float
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )

    def is_significant_move(self, threshold_pct: float) -> bool:
        """Return True when the price move exceeds the given threshold."""
        return abs(self.change_pct) >= threshold_pct


@dataclass(frozen=True)
class AlertRule:
    """Defines a price-change threshold for a specific ticker."""

    alert_id: str
    ticker: str
    threshold_pct: float
    webhook_url: str | None = None
