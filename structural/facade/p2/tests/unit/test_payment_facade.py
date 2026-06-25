"""Unit tests for PaymentFacade — every subsystem is mocked.

These tests prove the Facade orchestrates validation -> gateway -> repository
-> receipts correctly, independent of Stripe or MySQL (Dependency Inversion
in action: the Facade only knows about Protocols).
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.payment.application.facade import PaymentFacade
from src.payment.domain.entities import (
    Charge,
    CreditCard,
    Customer,
    Receipt,
    Transaction,
    TransactionStatus,
)
from src.payment.domain.exceptions import (
    CardDeclinedError,
    InvalidCardError,
    PaymentProcessingError,
    TransactionNotFoundError,
)


@pytest.fixture
def customer() -> Customer:
    return Customer(id="cus_1", name="Ada Lovelace", email="ada@example.com")


@pytest.fixture
def card() -> CreditCard:
    return CreditCard("4242424242424242", 12, 2099, "123", "Ada Lovelace")


@pytest.fixture
def mocks() -> dict[str, MagicMock]:
    return {
        "validator": MagicMock(),
        "gateway": MagicMock(),
        "repository": MagicMock(),
        "receipts": MagicMock(),
    }


@pytest.fixture
def facade(mocks: dict[str, MagicMock]) -> PaymentFacade:
    return PaymentFacade(
        validator=mocks["validator"],
        gateway=mocks["gateway"],
        repository=mocks["repository"],
        receipts=mocks["receipts"],
    )


def test_process_payment_success(
    facade: PaymentFacade,
    mocks: dict[str, MagicMock],
    customer: Customer,
    card: CreditCard,
) -> None:
    mocks["gateway"].charge.return_value = Charge(
        charge_id="ch_123", amount_cents=1000, currency="usd", created_at=None
    )
    mocks["receipts"].send_receipt.return_value = Receipt(
        receipt_id="rcpt_1", transaction_id="whatever", sent_to=customer.email
    )

    result = facade.process_payment(customer, card, 1000, "usd")

    assert result.status == TransactionStatus.APPROVED
    assert result.receipt_id == "rcpt_1"
    mocks["validator"].validate.assert_called_once_with(card)
    mocks["gateway"].charge.assert_called_once_with(card, 1000, "usd")
    assert mocks["repository"].save.call_count == 1
    assert mocks["repository"].update.call_count == 1
    mocks["receipts"].send_receipt.assert_called_once()


def test_process_payment_invalid_card_raises_and_saves_failed_transaction(
    facade: PaymentFacade,
    mocks: dict[str, MagicMock],
    customer: Customer,
    card: CreditCard,
) -> None:
    mocks["validator"].validate.side_effect = InvalidCardError("expired")

    with pytest.raises(InvalidCardError):
        facade.process_payment(customer, card, 1000, "usd")

    mocks["gateway"].charge.assert_not_called()
    mocks["repository"].save.assert_called_once()
    saved_transaction: Transaction = mocks["repository"].save.call_args[0][0]
    assert saved_transaction.status == TransactionStatus.FAILED


def test_process_payment_declined_card_raises_and_updates_transaction(
    facade: PaymentFacade,
    mocks: dict[str, MagicMock],
    customer: Customer,
    card: CreditCard,
) -> None:
    mocks["gateway"].charge.side_effect = CardDeclinedError("insufficient_funds", "")

    with pytest.raises(CardDeclinedError):
        facade.process_payment(customer, card, 1000, "usd")

    mocks["repository"].update.assert_called_once()
    updated_transaction: Transaction = mocks["repository"].update.call_args[0][0]
    assert updated_transaction.status == TransactionStatus.DECLINED
    mocks["receipts"].send_receipt.assert_not_called()


def test_process_payment_unexpected_gateway_error_wraps_in_processing_error(
    facade: PaymentFacade,
    mocks: dict[str, MagicMock],
    customer: Customer,
    card: CreditCard,
) -> None:
    mocks["gateway"].charge.side_effect = RuntimeError("network timeout")

    with pytest.raises(PaymentProcessingError):
        facade.process_payment(customer, card, 1000, "usd")

    updated_transaction: Transaction = mocks["repository"].update.call_args[0][0]
    assert updated_transaction.status == TransactionStatus.FAILED


def test_get_transaction_returns_transaction(
    facade: PaymentFacade, mocks: dict[str, MagicMock]
) -> None:
    transaction = Transaction.create("cus_1", 1000, "usd")
    mocks["repository"].find_by_id.return_value = transaction

    result = facade.get_transaction(transaction.id)

    assert result is transaction


def test_get_transaction_raises_when_not_found(
    facade: PaymentFacade, mocks: dict[str, MagicMock]
) -> None:
    mocks["repository"].find_by_id.return_value = None

    with pytest.raises(TransactionNotFoundError):
        facade.get_transaction("missing")


def test_refund_payment_success(
    facade: PaymentFacade, mocks: dict[str, MagicMock]
) -> None:
    transaction = Transaction.create("cus_1", 1000, "usd")
    transaction.approve("ch_123")
    mocks["repository"].find_by_id.return_value = transaction
    mocks["gateway"].refund.return_value = True

    result = facade.refund_payment(transaction.id)

    assert result.status == TransactionStatus.REFUNDED
    mocks["gateway"].refund.assert_called_once_with("ch_123")
    mocks["repository"].update.assert_called_once()


def test_refund_payment_raises_when_not_approved(
    facade: PaymentFacade, mocks: dict[str, MagicMock]
) -> None:
    transaction = Transaction.create("cus_1", 1000, "usd")
    mocks["repository"].find_by_id.return_value = transaction

    with pytest.raises(PaymentProcessingError, match="cannot refund"):
        facade.refund_payment(transaction.id)


def test_refund_payment_raises_when_gateway_refund_fails(
    facade: PaymentFacade, mocks: dict[str, MagicMock]
) -> None:
    transaction = Transaction.create("cus_1", 1000, "usd")
    transaction.approve("ch_123")
    mocks["repository"].find_by_id.return_value = transaction
    mocks["gateway"].refund.return_value = False

    with pytest.raises(PaymentProcessingError, match="refund failed"):
        facade.refund_payment(transaction.id)
