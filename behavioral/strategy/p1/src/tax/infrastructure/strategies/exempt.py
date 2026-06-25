"""Exempt tax strategy: zero tax for B2B exempt customers."""

from __future__ import annotations

from tax.domain.entities import Customer, Order, TaxBreakdown
from tax.domain.interfaces import TaxStrategy


class ExemptTaxStrategy(TaxStrategy):
    """Zero-tax strategy for B2B exempt orders.

    LSP: returns the same TaxBreakdown type with empty taxes list.
    """

    def calculate(self, order: Order, customer: Customer) -> TaxBreakdown:
        return TaxBreakdown.zero(order.subtotal, self.get_name())

    def get_name(self) -> str:
        return "exempt"

    def get_description(self) -> str:
        return "Tax exempt — B2B orders with valid exemption certificate"
