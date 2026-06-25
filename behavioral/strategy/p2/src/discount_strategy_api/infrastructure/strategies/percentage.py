"""PercentageDiscountStrategy — flat percentage off the order total."""

from __future__ import annotations

from discount_strategy_api.domain.entities import DiscountResult
from discount_strategy_api.domain.interfaces import DiscountStrategy


class PercentageDiscountStrategy(DiscountStrategy):
    def __init__(self, percentage: float) -> None:
        if not 0 <= percentage <= 100:
            raise ValueError(f"percentage must be between 0 and 100, got {percentage}")
        self._percentage = percentage

    def apply(self, original_total: float, quantity: int) -> DiscountResult:
        discount_amount = original_total * (self._percentage / 100)
        return DiscountResult(
            original_total=original_total,
            discount_amount=discount_amount,
            final_total=original_total - discount_amount,
            strategy_name=self.get_name(),
        )

    def get_name(self) -> str:
        return "percentage"

    def get_description(self) -> str:
        return f"{self._percentage:.0f}% off the order total"
