"""NoDiscountStrategy — the null object: no discount applied."""

from __future__ import annotations

from discount_strategy_api.domain.entities import DiscountResult
from discount_strategy_api.domain.interfaces import DiscountStrategy


class NoDiscountStrategy(DiscountStrategy):
    def apply(self, original_total: float, quantity: int) -> DiscountResult:
        return DiscountResult(
            original_total=original_total,
            discount_amount=0.0,
            final_total=original_total,
            strategy_name=self.get_name(),
        )

    def get_name(self) -> str:
        return "no_discount"

    def get_description(self) -> str:
        return "No discount applied"
