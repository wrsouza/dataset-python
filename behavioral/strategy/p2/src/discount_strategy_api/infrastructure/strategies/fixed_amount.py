"""FixedAmountDiscountStrategy — flat currency amount off, never going negative."""

from __future__ import annotations

from discount_strategy_api.domain.entities import DiscountResult
from discount_strategy_api.domain.interfaces import DiscountStrategy


class FixedAmountDiscountStrategy(DiscountStrategy):
    def __init__(self, amount: float) -> None:
        if amount < 0:
            raise ValueError(f"amount cannot be negative, got {amount}")
        self._amount = amount

    def apply(self, original_total: float, quantity: int) -> DiscountResult:
        discount_amount = min(self._amount, original_total)
        return DiscountResult(
            original_total=original_total,
            discount_amount=discount_amount,
            final_total=original_total - discount_amount,
            strategy_name=self.get_name(),
        )

    def get_name(self) -> str:
        return "fixed_amount"

    def get_description(self) -> str:
        return f"${self._amount:.2f} off the order total"
