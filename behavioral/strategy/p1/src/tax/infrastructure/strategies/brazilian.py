"""Brazilian tax strategy: ICMS 18% + PIS 0.65% + COFINS 3%."""

from __future__ import annotations

from decimal import Decimal

from tax.domain.entities import Customer, Order, TaxBreakdown, TaxLine
from tax.domain.interfaces import TaxStrategy

_ICMS_RATE = Decimal("0.18")
_PIS_RATE = Decimal("0.0065")
_COFINS_RATE = Decimal("0.03")


class BrazilianTaxStrategy(TaxStrategy):
    """Applies Brazilian federal and state taxes: ICMS, PIS, COFINS."""

    def calculate(self, order: Order, customer: Customer) -> TaxBreakdown:
        subtotal = order.subtotal
        icms = subtotal * _ICMS_RATE
        pis = subtotal * _PIS_RATE
        cofins = subtotal * _COFINS_RATE

        taxes = [
            TaxLine(
                name="ICMS",
                rate=_ICMS_RATE,
                amount=icms,
                description="Imposto sobre Circulação de Mercadorias e Serviços",
            ),
            TaxLine(
                name="PIS",
                rate=_PIS_RATE,
                amount=pis,
                description="Programa de Integração Social",
            ),
            TaxLine(
                name="COFINS",
                rate=_COFINS_RATE,
                amount=cofins,
                description="Contribuição para o Financiamento da Seguridade Social",
            ),
        ]
        total_tax = icms + pis + cofins
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
        return "brazil"

    def get_description(self) -> str:
        return "Brazilian tax: ICMS 18% + PIS 0.65% + COFINS 3%"
