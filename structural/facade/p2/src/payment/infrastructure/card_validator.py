from __future__ import annotations

from datetime import datetime

from src.payment.domain.entities import CreditCard
from src.payment.domain.exceptions import InvalidCardError

MIN_CARD_LENGTH = 13
MAX_CARD_LENGTH = 19
CVC_LENGTH = 3


class LuhnCardValidator:
    """Validates card number (Luhn checksum), expiry and CVC before charging.

    Kept entirely free of network calls — a card with bad data should never
    reach the Stripe API.
    """

    def validate(self, card: CreditCard) -> None:
        digits = card.number.replace(" ", "")
        if not digits.isdigit():
            raise InvalidCardError("card number must contain only digits")
        if not (MIN_CARD_LENGTH <= len(digits) <= MAX_CARD_LENGTH):
            raise InvalidCardError("card number has an invalid length")
        if not self._passes_luhn_check(digits):
            raise InvalidCardError("card number failed Luhn checksum")
        if len(card.cvc) != CVC_LENGTH or not card.cvc.isdigit():
            raise InvalidCardError("cvc must be 3 digits")
        self._ensure_not_expired(card)

    def _passes_luhn_check(self, digits: str) -> bool:
        total = 0
        for index, digit_char in enumerate(reversed(digits)):
            digit = int(digit_char)
            if index % 2 == 1:
                digit *= 2
                if digit > 9:
                    digit -= 9
            total += digit
        return total % 10 == 0

    def _ensure_not_expired(self, card: CreditCard) -> None:
        now = datetime.utcnow()
        if card.exp_year < now.year or (
            card.exp_year == now.year and card.exp_month < now.month
        ):
            raise InvalidCardError("card has expired")
