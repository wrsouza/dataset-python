"""TaxCalculator context — uses TaxStrategy via composition, swappable at runtime."""

from __future__ import annotations

from tax.domain.entities import Customer, Order, TaxBreakdown
from tax.domain.exceptions import NoStrategyConfiguredError
from tax.domain.interfaces import TaxStrategy


class TaxCalculator:
    """Context that delegates tax calculation to a pluggable TaxStrategy.

    DIP: depends on TaxStrategy ABC, not concrete implementations.
    Strategy can be changed at runtime via set_strategy().
    """

    def __init__(self, strategy: TaxStrategy | None = None) -> None:
        self._strategy: TaxStrategy | None = strategy

    def set_strategy(self, strategy: TaxStrategy) -> None:
        """Replace the current strategy at runtime."""
        self._strategy = strategy

    @property
    def current_strategy(self) -> TaxStrategy | None:
        return self._strategy

    def calculate(self, order: Order, customer: Customer) -> TaxBreakdown:
        """Delegate calculation to the configured strategy.

        Raises:
            NoStrategyConfiguredError: when no strategy has been set.
        """
        if self._strategy is None:
            raise NoStrategyConfiguredError()
        return self._strategy.calculate(order, customer)
