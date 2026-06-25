"""DiscountCalculator context — uses DiscountStrategy via composition,
swappable at runtime."""

from __future__ import annotations

from discount_strategy_api.domain.entities import DiscountResult
from discount_strategy_api.domain.exceptions import NoStrategyConfiguredError
from discount_strategy_api.domain.interfaces import DiscountStrategy


class DiscountCalculator:
    """Context that delegates discount calculation to a pluggable
    DiscountStrategy.

    DIP: depends on DiscountStrategy ABC, not concrete implementations.
    Strategy can be changed at runtime via set_strategy().
    """

    def __init__(self, strategy: DiscountStrategy | None = None) -> None:
        self._strategy: DiscountStrategy | None = strategy

    def set_strategy(self, strategy: DiscountStrategy) -> None:
        self._strategy = strategy

    @property
    def current_strategy(self) -> DiscountStrategy | None:
        return self._strategy

    def calculate(self, original_total: float, quantity: int) -> DiscountResult:
        """Delegate calculation to the configured strategy.

        Raises:
            NoStrategyConfiguredError: when no strategy has been set.
        """
        if self._strategy is None:
            raise NoStrategyConfiguredError()
        return self._strategy.apply(original_total, quantity)
