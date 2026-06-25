"""ConcreteCreators and ConcreteProducts for each payment gateway.

Each ConcreteCreator overrides create_payment_processor() to return
its specific ConcreteProduct (processor), keeping the Factory Method
contract.  Adding a new gateway = adding a new pair here, zero changes
to existing code (OCP).

All external-provider calls are mocked — no real API keys required.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from payment.domain.entities import (
    PaymentRequest,
    PaymentResult,
    PaymentStatus,
)
from payment.domain.interfaces import PaymentGatewayCreator, PaymentProcessor


# ── Stripe ────────────────────────────────────────────────────────────────────

class StripePaymentProcessor:
    """ConcreteProduct — mocked Stripe payment processor."""

    def process(self, request: PaymentRequest) -> PaymentResult:
        # Mock: simulate Stripe charge API response
        txn_id = f"stripe_txn_{uuid.uuid4().hex[:12]}"
        return PaymentResult(
            transaction_id=txn_id,
            gateway="stripe",
            status=PaymentStatus.COMPLETED,
            amount=request.amount,
            currency=request.currency,
            gateway_reference=f"ch_{uuid.uuid4().hex[:24]}",
        )

    def refund(self, transaction_id: str, amount: float) -> PaymentResult:
        return PaymentResult(
            transaction_id=f"stripe_refund_{uuid.uuid4().hex[:12]}",
            gateway="stripe",
            status=PaymentStatus.REFUNDED,
            amount=amount,
            currency="USD",
            gateway_reference=f"re_{uuid.uuid4().hex[:24]}",
        )


class StripeGatewayCreator(PaymentGatewayCreator):
    """ConcreteCreator — creates a StripePaymentProcessor."""

    def create_payment_processor(self) -> PaymentProcessor:
        return StripePaymentProcessor()  # type: ignore[return-value]

    def get_gateway_name(self) -> str:
        return "Stripe"


# ── PayPal ────────────────────────────────────────────────────────────────────

class PayPalPaymentProcessor:
    """ConcreteProduct — mocked PayPal payment processor."""

    def process(self, request: PaymentRequest) -> PaymentResult:
        # Mock: simulate PayPal Orders API response
        txn_id = f"paypal_txn_{uuid.uuid4().hex[:12]}"
        return PaymentResult(
            transaction_id=txn_id,
            gateway="paypal",
            status=PaymentStatus.COMPLETED,
            amount=request.amount,
            currency=request.currency,
            gateway_reference=f"PAYID-{uuid.uuid4().hex[:20].upper()}",
        )

    def refund(self, transaction_id: str, amount: float) -> PaymentResult:
        return PaymentResult(
            transaction_id=f"paypal_refund_{uuid.uuid4().hex[:12]}",
            gateway="paypal",
            status=PaymentStatus.REFUNDED,
            amount=amount,
            currency="USD",
            gateway_reference=f"REFUND-{uuid.uuid4().hex[:16].upper()}",
        )


class PayPalGatewayCreator(PaymentGatewayCreator):
    """ConcreteCreator — creates a PayPalPaymentProcessor."""

    def create_payment_processor(self) -> PaymentProcessor:
        return PayPalPaymentProcessor()  # type: ignore[return-value]

    def get_gateway_name(self) -> str:
        return "PayPal"


# ── PIX ───────────────────────────────────────────────────────────────────────

class PIXPaymentProcessor:
    """ConcreteProduct — mocked Brazilian PIX instant payment processor."""

    def process(self, request: PaymentRequest) -> PaymentResult:
        # Mock: simulate Banco Central PIX API response
        txn_id = f"pix_txn_{uuid.uuid4().hex[:12]}"
        return PaymentResult(
            transaction_id=txn_id,
            gateway="pix",
            status=PaymentStatus.COMPLETED,
            amount=request.amount,
            currency=request.currency,
            # PIX end-to-end ID format (E + 32 chars)
            gateway_reference=f"E{''.join(str(uuid.uuid4().int)[:32])}",
        )

    def refund(self, transaction_id: str, amount: float) -> PaymentResult:
        # PIX devolution
        return PaymentResult(
            transaction_id=f"pix_dev_{uuid.uuid4().hex[:12]}",
            gateway="pix",
            status=PaymentStatus.REFUNDED,
            amount=amount,
            currency="BRL",
            gateway_reference=f"D{''.join(str(uuid.uuid4().int)[:32])}",
        )


class PIXGatewayCreator(PaymentGatewayCreator):
    """ConcreteCreator — creates a PIXPaymentProcessor."""

    def create_payment_processor(self) -> PaymentProcessor:
        return PIXPaymentProcessor()  # type: ignore[return-value]

    def get_gateway_name(self) -> str:
        return "PIX"


# ── Registry ─────────────────────────────────────────────────────────────────

GATEWAY_REGISTRY: dict[str, PaymentGatewayCreator] = {
    "stripe": StripeGatewayCreator(),
    "paypal": PayPalGatewayCreator(),
    "pix": PIXGatewayCreator(),
}
