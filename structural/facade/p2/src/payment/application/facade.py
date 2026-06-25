"""
PaymentFacade — single entry point for the complete payment processing workflow.

Hides the complexity of card validation, the Stripe gateway, MySQL persistence
and receipt delivery. Client code (the Flask routes) calls only this class.
"""

from __future__ import annotations

import logging

from src.payment.domain.entities import (
    CreditCard,
    Customer,
    PaymentResult,
    Transaction,
    TransactionId,
    TransactionStatus,
)
from src.payment.domain.exceptions import (
    CardDeclinedError,
    InvalidCardError,
    PaymentProcessingError,
    TransactionNotFoundError,
)
from src.payment.domain.interfaces import (
    CardValidatorProtocol,
    PaymentGatewayProtocol,
    ReceiptServiceProtocol,
    TransactionRepositoryProtocol,
)

logger = logging.getLogger(__name__)


class PaymentFacade:
    """
    Facade that orchestrates validation, charging, persistence and receipts.

    Client code only depends on this class — not on Stripe, MySQL or the
    receipt service directly. Each subsystem is injected via its Protocol,
    so any implementation can be swapped without touching this class
    (Open/Closed + Dependency Inversion).
    """

    def __init__(
        self,
        validator: CardValidatorProtocol,
        gateway: PaymentGatewayProtocol,
        repository: TransactionRepositoryProtocol,
        receipts: ReceiptServiceProtocol,
    ) -> None:
        self._validator = validator
        self._gateway = gateway
        self._repository = repository
        self._receipts = receipts

    def process_payment(
        self,
        customer: Customer,
        card: CreditCard,
        amount_cents: int,
        currency: str = "usd",
    ) -> PaymentResult:
        """
        Execute the full payment workflow.

        Steps:
          1. Validate card data (Luhn, expiry, CVC) — no network call.
          2. Create and persist a PENDING transaction.
          3. Charge the card via the Stripe gateway.
          4. Update the transaction to APPROVED/DECLINED.
          5. Send a receipt on success.
        """
        transaction = Transaction.create(customer.id, amount_cents, currency)

        try:
            self._validator.validate(card)
        except InvalidCardError as exc:
            transaction.fail(exc.reason)
            self._repository.save(transaction)
            logger.warning("Transaction %s rejected: %s", transaction.id, exc.reason)
            raise

        self._repository.save(transaction)
        logger.info("Transaction %s created (pending)", transaction.id)

        try:
            charge = self._gateway.charge(card, amount_cents, currency)
        except CardDeclinedError as exc:
            transaction.decline(exc.reason)
            self._repository.update(transaction)
            logger.info("Transaction %s declined: %s", transaction.id, exc.reason)
            raise CardDeclinedError(exc.reason, transaction.id) from exc
        except Exception as exc:
            transaction.fail(str(exc))
            self._repository.update(transaction)
            logger.error("Transaction %s failed: %s", transaction.id, exc)
            raise PaymentProcessingError(str(exc), transaction.id) from exc

        transaction.approve(charge.charge_id)
        self._repository.update(transaction)
        logger.info(
            "Transaction %s approved (charge %s)", transaction.id, charge.charge_id
        )

        receipt = self._receipts.send_receipt(transaction, customer.email)

        return PaymentResult(
            transaction_id=transaction.id,
            status=transaction.status,
            amount_cents=transaction.amount_cents,
            currency=transaction.currency,
            receipt_id=receipt.receipt_id,
            message="Payment approved.",
        )

    def get_transaction(self, transaction_id: TransactionId) -> Transaction:
        """Retrieve a transaction by id."""
        transaction = self._repository.find_by_id(transaction_id)
        if transaction is None:
            raise TransactionNotFoundError(transaction_id)
        return transaction

    def refund_payment(self, transaction_id: TransactionId) -> PaymentResult:
        """Refund a previously approved transaction."""
        transaction = self.get_transaction(transaction_id)

        if transaction.status != TransactionStatus.APPROVED:
            raise PaymentProcessingError(
                f"cannot refund transaction in status {transaction.status.value}",
                transaction.id,
            )
        if transaction.charge_id is None:
            raise PaymentProcessingError(
                "transaction has no associated charge", transaction.id
            )

        refunded = self._gateway.refund(transaction.charge_id)
        if not refunded:
            raise PaymentProcessingError("refund failed at gateway", transaction.id)

        transaction.refund()
        self._repository.update(transaction)
        logger.info("Transaction %s refunded", transaction.id)

        return PaymentResult(
            transaction_id=transaction.id,
            status=transaction.status,
            amount_cents=transaction.amount_cents,
            currency=transaction.currency,
            receipt_id=None,
            message="Payment refunded.",
        )
