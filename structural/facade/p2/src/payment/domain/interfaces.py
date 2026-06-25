from __future__ import annotations

from typing import Protocol

from src.payment.domain.entities import (
    Charge,
    CreditCard,
    Receipt,
    Transaction,
    TransactionId,
)


class CardValidatorProtocol(Protocol):
    """Validates raw card data before any external call is made."""

    def validate(self, card: CreditCard) -> None:
        """Raise InvalidCardError when the card data is not acceptable."""
        ...


class PaymentGatewayProtocol(Protocol):
    """Talks to the external payment provider (Stripe)."""

    def charge(self, card: CreditCard, amount_cents: int, currency: str) -> Charge: ...

    def refund(self, charge_id: str) -> bool: ...


class TransactionRepositoryProtocol(Protocol):
    """Persists and retrieves payment transactions."""

    def save(self, transaction: Transaction) -> None: ...

    def find_by_id(self, transaction_id: TransactionId) -> Transaction | None: ...

    def update(self, transaction: Transaction) -> None: ...


class ReceiptServiceProtocol(Protocol):
    """Sends a receipt email/notification after a successful payment."""

    def send_receipt(
        self, transaction: Transaction, customer_email: str
    ) -> Receipt: ...
