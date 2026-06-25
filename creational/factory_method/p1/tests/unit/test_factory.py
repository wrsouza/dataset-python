"""Unit tests for the Factory Method pattern in P1 — Payment Gateway."""
from __future__ import annotations

import pytest

from payment.domain.entities import (
    PaymentRequest,
    PaymentResult,
    PaymentStatus,
)
from payment.domain.interfaces import PaymentGatewayCreator, PaymentProcessor
from payment.infrastructure.creators import (
    GATEWAY_REGISTRY,
    PIXGatewayCreator,
    PayPalGatewayCreator,
    StripeGatewayCreator,
)


# ── Factory Method contract tests ─────────────────────────────────────────────

class TestStripeGatewayCreator:
    def test_create_returns_payment_processor(self) -> None:
        creator = StripeGatewayCreator()
        processor = creator.create_payment_processor()
        assert isinstance(processor, PaymentProcessor)

    def test_gateway_name(self) -> None:
        assert StripeGatewayCreator().get_gateway_name() == "Stripe"

    def test_process_returns_completed_result(self, sample_request: PaymentRequest) -> None:
        processor = StripeGatewayCreator().create_payment_processor()
        result = processor.process(sample_request)
        assert result.status == PaymentStatus.COMPLETED
        assert result.gateway == "stripe"
        assert result.amount == sample_request.amount
        assert result.currency == sample_request.currency

    def test_transaction_id_is_unique(self, sample_request: PaymentRequest) -> None:
        processor = StripeGatewayCreator().create_payment_processor()
        r1 = processor.process(sample_request)
        r2 = processor.process(sample_request)
        assert r1.transaction_id != r2.transaction_id


class TestPayPalGatewayCreator:
    def test_create_returns_payment_processor(self) -> None:
        processor = PayPalGatewayCreator().create_payment_processor()
        assert isinstance(processor, PaymentProcessor)

    def test_gateway_name(self) -> None:
        assert PayPalGatewayCreator().get_gateway_name() == "PayPal"

    def test_process_completed(self, sample_request: PaymentRequest) -> None:
        processor = PayPalGatewayCreator().create_payment_processor()
        result = processor.process(sample_request)
        assert result.status == PaymentStatus.COMPLETED
        assert result.gateway == "paypal"


class TestPIXGatewayCreator:
    def test_create_returns_payment_processor(self) -> None:
        processor = PIXGatewayCreator().create_payment_processor()
        assert isinstance(processor, PaymentProcessor)

    def test_gateway_name(self) -> None:
        assert PIXGatewayCreator().get_gateway_name() == "PIX"

    def test_process_completed(self, sample_request: PaymentRequest) -> None:
        processor = PIXGatewayCreator().create_payment_processor()
        result = processor.process(sample_request)
        assert result.status == PaymentStatus.COMPLETED
        assert result.gateway == "pix"


# ── OCP — new gateway does not break existing tests ───────────────────────────

class TestGatewayRegistry:
    def test_all_gateways_registered(self) -> None:
        assert set(GATEWAY_REGISTRY.keys()) == {"stripe", "paypal", "pix"}

    def test_each_creator_produces_valid_processor(
        self, sample_request: PaymentRequest
    ) -> None:
        for slug, creator in GATEWAY_REGISTRY.items():
            processor = creator.create_payment_processor()
            result = processor.process(sample_request)
            assert result.is_successful, f"{slug} should return completed status"


# ── DIP — use case with a fake creator ───────────────────────────────────────

class FakeGatewayCreator(PaymentGatewayCreator):
    """Test double demonstrating DIP: use cases accept any creator."""

    def create_payment_processor(self) -> PaymentProcessor:
        class FakeProcessor:
            def process(self, req: PaymentRequest) -> PaymentResult:
                from datetime import datetime

                return PaymentResult(
                    transaction_id="fake_txn_001",
                    gateway="fake",
                    status=PaymentStatus.COMPLETED,
                    amount=req.amount,
                    currency=req.currency,
                    created_at=datetime.utcnow(),
                )

            def refund(self, txn_id: str, amount: float) -> PaymentResult:
                from datetime import datetime

                return PaymentResult(
                    transaction_id="fake_refund_001",
                    gateway="fake",
                    status=PaymentStatus.REFUNDED,
                    amount=amount,
                    currency="USD",
                    created_at=datetime.utcnow(),
                )

        return FakeProcessor()  # type: ignore[return-value]

    def get_gateway_name(self) -> str:
        return "Fake"


class TestDependencyInversion:
    def test_use_case_accepts_any_creator(self, sample_request: PaymentRequest) -> None:
        from unittest.mock import MagicMock

        from payment.application.use_cases import ProcessPaymentUseCase

        repo = MagicMock()
        use_case = ProcessPaymentUseCase(creator=FakeGatewayCreator(), repository=repo)
        result = use_case.execute(sample_request)
        assert result.transaction_id == "fake_txn_001"
        repo.save.assert_called_once()


# ── PaymentRequest validation ─────────────────────────────────────────────────

class TestPaymentRequest:
    def test_negative_amount_raises(self) -> None:
        with pytest.raises(ValueError, match="positive"):
            PaymentRequest(amount=-1.0, currency="USD")

    def test_zero_amount_raises(self) -> None:
        with pytest.raises(ValueError, match="positive"):
            PaymentRequest(amount=0.0, currency="USD")

    def test_invalid_currency_raises(self) -> None:
        with pytest.raises(ValueError, match="ISO 4217"):
            PaymentRequest(amount=10.0, currency="US")
