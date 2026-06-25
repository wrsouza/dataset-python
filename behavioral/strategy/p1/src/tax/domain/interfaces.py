"""Strategy ABC for the tax calculation domain."""

from __future__ import annotations

from abc import ABC, abstractmethod

from tax.domain.entities import Customer, Order, TaxBreakdown


class TaxStrategy(ABC):
    """Abstract base for all tax calculation strategies.

    OCP: Add new jurisdiction = new subclass, no existing code changes.
    LSP: All subclasses return TaxBreakdown and honor the same contract.
    """

    @abstractmethod
    def calculate(self, order: Order, customer: Customer) -> TaxBreakdown:
        """Calculate taxes for the given order and customer.

        Args:
            order: The order to tax.
            customer: The customer placing the order.

        Returns:
            A TaxBreakdown with all tax lines and totals.
        """
        ...

    @abstractmethod
    def get_name(self) -> str:
        """Return the human-readable name of this strategy."""
        ...

    @abstractmethod
    def get_description(self) -> str:
        """Return a description of the tax rules applied."""
        ...
