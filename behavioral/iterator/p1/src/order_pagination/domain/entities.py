"""Core entities for the order cursor-pagination domain."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Order:
    """A single order — the element type this Iterator traverses."""

    order_id: int
    customer: str
    amount: float
    created_at: datetime


@dataclass(frozen=True)
class OrdersPage:
    """One page of orders plus the cursor to fetch the next page, if any."""

    items: list[Order]
    next_cursor: str | None
