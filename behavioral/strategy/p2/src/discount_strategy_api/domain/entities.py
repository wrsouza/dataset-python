"""Domain entities for the Discount Strategy API."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DiscountResult:
    """Immutable outcome of applying a discount strategy to an order."""

    original_total: float
    discount_amount: float
    final_total: float
    strategy_name: str

    def __post_init__(self) -> None:
        if self.original_total < 0:
            raise ValueError("original_total cannot be negative")
        if self.discount_amount < 0:
            raise ValueError("discount_amount cannot be negative")
