"""Domain exceptions for the Discount Strategy API."""

from __future__ import annotations


class InvalidStrategyError(Exception):
    """Raised when a strategy name is not registered."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Unknown discount strategy '{name}'")
        self.name = name


class NoStrategyConfiguredError(Exception):
    """Raised when the DiscountCalculator is asked to calculate without a strategy."""

    def __init__(self) -> None:
        super().__init__("No discount strategy configured")
