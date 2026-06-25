"""Domain entities for the Django Signals System."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class OrderEvent:
    """Immutable value object broadcast whenever an order is created or
    changes status."""

    order_id: str
    status: str
    total: float
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
