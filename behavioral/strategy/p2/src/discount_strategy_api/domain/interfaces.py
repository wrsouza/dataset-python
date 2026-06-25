"""Strategy ABC for the Discount Strategy API."""

from __future__ import annotations

from abc import ABC, abstractmethod

from discount_strategy_api.domain.entities import DiscountResult


class DiscountStrategy(ABC):
    """Abstract base for all discount strategies.

    OCP: add a new discount rule = new subclass, no existing code changes.
    LSP: all subclasses return DiscountResult and honor the same contract.
    """

    @abstractmethod
    def apply(self, original_total: float, quantity: int) -> DiscountResult:
        """Apply this strategy's discount rule to an order."""
        ...

    @abstractmethod
    def get_name(self) -> str:
        """Return the canonical name of this strategy."""
        ...

    @abstractmethod
    def get_description(self) -> str:
        """Return a human-readable description of the discount rule."""
        ...
