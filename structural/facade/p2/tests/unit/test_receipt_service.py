from __future__ import annotations

from src.payment.domain.entities import Transaction
from src.payment.infrastructure.receipt_service import EmailReceiptService


def test_send_receipt_returns_receipt_for_transaction() -> None:
    service = EmailReceiptService()
    transaction = Transaction.create("cus_1", 1000, "usd")

    receipt = service.send_receipt(transaction, "ada@example.com")

    assert receipt.transaction_id == transaction.id
    assert receipt.sent_to == "ada@example.com"
    assert receipt.receipt_id.startswith("rcpt_")
