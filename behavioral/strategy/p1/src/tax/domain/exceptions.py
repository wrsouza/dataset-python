"""Domain-specific exceptions for tax calculation."""

from __future__ import annotations


class TaxDomainError(Exception):
    """Base exception for tax domain errors."""


class OrderNotFoundError(TaxDomainError):
    def __init__(self, order_id: str) -> None:
        self.order_id = order_id
        super().__init__(f"Order '{order_id}' not found")


class CustomerNotFoundError(TaxDomainError):
    def __init__(self, customer_id: str) -> None:
        self.customer_id = customer_id
        super().__init__(f"Customer '{customer_id}' not found")


class InvalidStrategyError(TaxDomainError):
    def __init__(self, strategy_name: str) -> None:
        self.strategy_name = strategy_name
        super().__init__(f"Unknown tax strategy: '{strategy_name}'")


class NoStrategyConfiguredError(TaxDomainError):
    def __init__(self) -> None:
        super().__init__("No tax strategy configured. Call set_strategy() first.")
