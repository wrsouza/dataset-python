from __future__ import annotations

import logging
from datetime import datetime
from uuid import uuid4

from src.order.domain.entities import (
    OrderId,
    PaymentCharge,
    PaymentMethod,
    PaymentStatus,
)
from src.order.domain.exceptions import PaymentDeclinedError

logger = logging.getLogger(__name__)


class MockPaymentService:
    """
    Mock payment service that simulates a payment gateway.

    In production this would wrap Stripe / Adyen / etc.
    Declines cards ending in '0000' to allow testing failure paths.
    """

    def charge(
        self,
        amount: float,
        payment_method: PaymentMethod,
        order_id: OrderId,
    ) -> PaymentCharge:
        logger.info(
            "Processing charge of %.2f for order %s with card %s",
            amount,
            order_id,
            payment_method.card_last_four,
        )

        if payment_method.card_last_four == "0000":
            raise PaymentDeclinedError(
                reason="Insufficient funds",
                order_id=order_id,
            )

        charge_id = f"ch_{uuid4().hex[:16]}"
        return PaymentCharge(
            charge_id=charge_id,
            amount=amount,
            status=PaymentStatus.APPROVED,
            transaction_at=datetime.utcnow(),
        )

    def refund(self, charge_id: str) -> bool:
        logger.info("Refunding charge %s", charge_id)
        return True
