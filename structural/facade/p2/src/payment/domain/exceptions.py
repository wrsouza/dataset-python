from __future__ import annotations


class PaymentError(Exception):
    """Base class for all payment domain errors."""


class InvalidCardError(PaymentError):
    """Raised when card data fails validation before reaching Stripe."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Invalid card: {reason}")


class CardDeclinedError(PaymentError):
    """Raised when Stripe declines the charge."""

    def __init__(self, reason: str, transaction_id: str) -> None:
        self.reason = reason
        self.transaction_id = transaction_id
        super().__init__(f"Card declined: {reason}")


class TransactionNotFoundError(PaymentError):
    """Raised when a transaction id does not exist in the repository."""

    def __init__(self, transaction_id: str) -> None:
        self.transaction_id = transaction_id
        super().__init__(f"Transaction not found: {transaction_id}")


class PaymentProcessingError(PaymentError):
    """Raised for unexpected failures during the payment workflow."""

    def __init__(self, reason: str, transaction_id: str | None = None) -> None:
        self.reason = reason
        self.transaction_id = transaction_id
        super().__init__(f"Payment processing failed: {reason}")
