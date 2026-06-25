from __future__ import annotations

import pytest

from src.payment.domain.entities import CreditCard
from src.payment.domain.exceptions import InvalidCardError
from src.payment.infrastructure.card_validator import LuhnCardValidator


@pytest.fixture
def validator() -> LuhnCardValidator:
    return LuhnCardValidator()


def test_validate_accepts_valid_card(validator: LuhnCardValidator) -> None:
    card = CreditCard("4242424242424242", 12, 2099, "123", "Ada Lovelace")
    validator.validate(card)  # should not raise


def test_validate_rejects_non_digit_number(validator: LuhnCardValidator) -> None:
    card = CreditCard("4242-4242-4242-4242", 12, 2099, "123", "Ada Lovelace")
    with pytest.raises(InvalidCardError, match="only digits"):
        validator.validate(card)


def test_validate_rejects_short_number(validator: LuhnCardValidator) -> None:
    card = CreditCard("4242", 12, 2099, "123", "Ada Lovelace")
    with pytest.raises(InvalidCardError, match="invalid length"):
        validator.validate(card)


def test_validate_rejects_failed_luhn_checksum(validator: LuhnCardValidator) -> None:
    card = CreditCard("4242424242424241", 12, 2099, "123", "Ada Lovelace")
    with pytest.raises(InvalidCardError, match="Luhn"):
        validator.validate(card)


def test_validate_rejects_bad_cvc(validator: LuhnCardValidator) -> None:
    card = CreditCard("4242424242424242", 12, 2099, "12", "Ada Lovelace")
    with pytest.raises(InvalidCardError, match="cvc"):
        validator.validate(card)


def test_validate_rejects_expired_card(validator: LuhnCardValidator) -> None:
    card = CreditCard("4242424242424242", 1, 2000, "123", "Ada Lovelace")
    with pytest.raises(InvalidCardError, match="expired"):
        validator.validate(card)
