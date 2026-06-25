"""Domain entities for Price Alerts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class PriceEvent:
    """Immutable value object representing a price change."""

    product_id: str
    old_price: float
    new_price: float
    change_pct: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(tz=UTC))

    @classmethod
    def from_prices(
        cls, product_id: str, old_price: float, new_price: float
    ) -> PriceEvent:
        change_pct = ((new_price - old_price) / old_price) * 100 if old_price else 0.0
        return cls(
            product_id=product_id,
            old_price=old_price,
            new_price=new_price,
            change_pct=round(change_pct, 4),
        )

    def exceeds_threshold(self, threshold: float) -> bool:
        return abs(self.change_pct) >= threshold


@dataclass
class Subscription:
    """Maps an observer to a product with a notification threshold."""

    subscription_id: str
    observer_id: str
    product_id: str
    threshold: float
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))
    is_active: bool = True


@dataclass
class AlertRecord:
    """Persisted record of a triggered alert."""

    record_id: str
    subscription_id: str
    product_id: str
    old_price: float
    new_price: float
    change_pct: float
    channel: str
    triggered_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))
