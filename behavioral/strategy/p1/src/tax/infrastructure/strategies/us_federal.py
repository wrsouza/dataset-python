"""US Federal tax strategy: federal rate + state rate."""

from __future__ import annotations

from decimal import Decimal

from tax.domain.entities import Customer, Order, TaxBreakdown, TaxLine
from tax.domain.interfaces import TaxStrategy

# Default US federal rate (simplified for demo)
_FEDERAL_RATE = Decimal("0.10")

# State rates by state code (simplified subset)
_STATE_RATES: dict[str, Decimal] = {
    "CA": Decimal("0.0725"),
    "NY": Decimal("0.08"),
    "TX": Decimal("0.0625"),
    "FL": Decimal("0.06"),
    "WA": Decimal("0.065"),
    "DEFAULT": Decimal("0.05"),
}


class USFederalTaxStrategy(TaxStrategy):
    """Applies US federal income tax and state sales tax."""

    def __init__(self, state_code: str = "DEFAULT") -> None:
        self._state_code = state_code.upper()

    def calculate(self, order: Order, customer: Customer) -> TaxBreakdown:
        subtotal = order.subtotal
        federal_rate = _FEDERAL_RATE
        state_rate = _STATE_RATES.get(self._state_code, _STATE_RATES["DEFAULT"])

        federal_tax = subtotal * federal_rate
        state_tax = subtotal * state_rate

        taxes = [
            TaxLine(
                name="US Federal Tax",
                rate=federal_rate,
                amount=federal_tax,
                description="US federal income tax",
            ),
            TaxLine(
                name=f"State Tax ({self._state_code})",
                rate=state_rate,
                amount=state_tax,
                description=f"State sales tax for {self._state_code}",
            ),
        ]
        total_tax = federal_tax + state_tax
        total = subtotal + total_tax
        effective_rate = total_tax / subtotal if subtotal else Decimal("0")

        return TaxBreakdown(
            subtotal=subtotal,
            taxes=taxes,
            total=total,
            effective_rate=effective_rate,
            strategy_used=self.get_name(),
        )

    def get_name(self) -> str:
        return "us"

    def get_description(self) -> str:
        return f"US Federal {_FEDERAL_RATE:.0%} + State ({self._state_code}) tax"
