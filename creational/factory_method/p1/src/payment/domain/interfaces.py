"""Domain interfaces for the Payment Gateway Factory pattern.

Defines the Creator ABC and Product Protocol following Factory Method.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

from payment.domain.entities import PaymentResult, PaymentRequest


@runtime_checkable
class PaymentProcessor(Protocol):
    """Product interface — every concrete processor must satisfy this contract."""

    def process(self, request: PaymentRequest) -> PaymentResult:
        """Process a payment and return the result.

        Args:
            request: The payment details including amount, currency, and metadata.

        Returns:
            PaymentResult with status and transaction reference.
        """
        ...

    def refund(self, transaction_id: str, amount: float) -> PaymentResult:
        """Refund a previously completed transaction.

        Args:
            transaction_id: The original transaction identifier.
            amount: Amount to refund (must be <= original amount).

        Returns:
            PaymentResult for the refund operation.
        """
        ...


class PaymentGatewayCreator(ABC):
    """Creator — declares the factory method that subclasses override.

    The Creator knows nothing about which concrete PaymentProcessor will be
    created; it only depends on the PaymentProcessor Protocol (DIP).
    Each new gateway is added by creating a new ConcreteCreator without
    modifying this class (OCP).
    """

    @abstractmethod
    def create_payment_processor(self) -> PaymentProcessor:
        """Factory method: returns a PaymentProcessor for this gateway.

        Subclasses decide which ConcreteProduct to instantiate.
        """
        ...

    def get_gateway_name(self) -> str:
        """Return a human-readable name for this gateway.

        Subclasses should override to provide an accurate name.
        """
        return self.__class__.__name__.replace("GatewayCreator", "")
