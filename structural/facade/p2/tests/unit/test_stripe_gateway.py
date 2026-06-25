from __future__ import annotations

import pytest

from src.payment.domain.entities import CreditCard
from src.payment.domain.exceptions import CardDeclinedError
from src.payment.infrastructure.stripe_gateway import MockStripeGateway


@pytest.fixture
def gateway() -> MockStripeGateway:
    return MockStripeGateway()


def test_charge_returns_charge_for_valid_card(gateway: MockStripeGateway) -> None:
    card = CreditCard("4242424242424242", 12, 2099, "123", "Ada Lovelace")
    charge = gateway.charge(card, 1000, "usd")

    assert charge.amount_cents == 1000
    assert charge.currency == "usd"
    assert charge.charge_id.startswith("ch_mock_")


def test_charge_raises_for_declined_card(gateway: MockStripeGateway) -> None:
    card = CreditCard("4000000000000002", 12, 2099, "123", "Ada Lovelace")
    with pytest.raises(CardDeclinedError):
        gateway.charge(card, 1000, "usd")


def test_refund_returns_true(gateway: MockStripeGateway) -> None:
    assert gateway.refund("ch_mock_abc123") is True
