from __future__ import annotations

import logging
from uuid import uuid4

from src.payment.domain.entities import Receipt, Transaction

logger = logging.getLogger(__name__)


class EmailReceiptService:
    """Sends a payment receipt by email.

    Real SMTP/SES integration is intentionally out of scope for this
    educational project — sending is simulated and logged, matching the
    mocking approach already used for the Stripe gateway in tests.
    """

    def send_receipt(self, transaction: Transaction, customer_email: str) -> Receipt:
        receipt = Receipt(
            receipt_id=f"rcpt_{uuid4().hex[:16]}",
            transaction_id=transaction.id,
            sent_to=customer_email,
        )
        logger.info(
            "Receipt %s sent to %s for transaction %s",
            receipt.receipt_id,
            customer_email,
            transaction.id,
        )
        return receipt
