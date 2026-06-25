"""BulkQuantityDiscountStrategy — percentage off when quantity meets a threshold."""

from __future__ import annotations

from discount_strategy_api.domain.entities import DiscountResult
from discount_strategy_api.domain.interfaces import DiscountStrategy


class BulkQuantityDiscountStrategy(DiscountStrategy):
    def __init__(self, threshold: int, percentage: float) -> None:
        if threshold < 1:
            raise ValueError(f"threshold must be >= 1, got {threshold}")
        if not 0 <= percentage <= 100:
            raise ValueError(f"percentage must be between 0 and 100, got {percentage}")
        self._threshold = threshold
        self._percentage = percentage

    def apply(self, original_total: float, quantity: int) -> DiscountResult:
        if quantity < self._threshold:
            discount_amount = 0.0
        else:
            discount_amount = original_total * (self._percentage / 100)
        return DiscountResult(
            original_total=original_total,
            discount_amount=discount_amount,
            final_total=original_total - discount_amount,
            strategy_name=self.get_name(),
        )

    def get_name(self) -> str:
        return "bulk_quantity"

    def get_description(self) -> str:
        return f"{self._percentage:.0f}% off when buying {self._threshold}+ units"
