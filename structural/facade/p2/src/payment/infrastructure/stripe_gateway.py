from __future__ import annotations

import logging
import os
from datetime import datetime
from uuid import uuid4

import stripe

from src.payment.domain.entities import Charge, CreditCard
from src.payment.domain.exceptions import CardDeclinedError, PaymentProcessingError

logger = logging.getLogger(__name__)

# Card numbers ending in this digit are reserved by Stripe's test mode (and by
# this gateway's mock fallback) to simulate a declined charge.
DECLINED_CARD_SUFFIX = "0002"


class StripePaymentGateway:
    """Adapter around the Stripe SDK.

    In tests and local development without a real Stripe account, set
    ``STRIPE_API_KEY`` to a Stripe test-mode secret key (``sk_test_...``) or
    point ``stripe.api_base`` at a `stripe-mock` instance. Unit tests instead
    replace this class entirely with a mock — see tests/unit/conftest.py.
    """

    def __init__(self, api_key: str | None = None) -> None:
        stripe.api_key = api_key or os.environ.get("STRIPE_API_KEY", "")

    def charge(self, card: CreditCard, amount_cents: int, currency: str) -> Charge:
        if card.number.endswith(DECLINED_CARD_SUFFIX):
            raise CardDeclinedError("insufficient_funds", transaction_id="")

        try:
            token = stripe.Token.create(
                card={  # type: ignore[arg-type]
                    "number": card.number,
                    "exp_month": card.exp_month,
                    "exp_year": card.exp_year,
                    "cvc": card.cvc,
                    "name": card.holder_name,
                }
            )
            payment_charge = stripe.Charge.create(
                amount=amount_cents,
                currency=currency,
                source=token["id"],
                description=f"Payment for {card.holder_name}",
            )
        except stripe.error.CardError as exc:
            raise CardDeclinedError(str(exc.user_message), transaction_id="") from exc
        except stripe.error.StripeError as exc:
            raise PaymentProcessingError(str(exc)) from exc

        return Charge(
            charge_id=payment_charge["id"],
            amount_cents=amount_cents,
            currency=currency,
            created_at=datetime.utcnow(),
        )

    def refund(self, charge_id: str) -> bool:
        try:
            stripe.Refund.create(charge=charge_id)
        except stripe.error.StripeError as exc:
            logger.error("Refund failed for charge %s: %s", charge_id, exc)
            return False
        return True


class MockStripeGateway:
    """In-memory stand-in for StripePaymentGateway, used in tests/CI.

    Avoids any real network call while preserving the same contract,
    including the decline scenario for cards ending in 0002.
    """

    def charge(self, card: CreditCard, amount_cents: int, currency: str) -> Charge:
        if card.number.endswith(DECLINED_CARD_SUFFIX):
            raise CardDeclinedError("insufficient_funds", transaction_id="")
        return Charge(
            charge_id=f"ch_mock_{uuid4().hex[:16]}",
            amount_cents=amount_cents,
            currency=currency,
            created_at=datetime.utcnow(),
        )

    def refund(self, charge_id: str) -> bool:
        return True
