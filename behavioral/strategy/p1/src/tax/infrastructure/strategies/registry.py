"""Strategy registry — maps string keys to TaxStrategy instances."""

from __future__ import annotations

from tax.domain.entities import CustomerCountry
from tax.domain.exceptions import InvalidStrategyError
from tax.domain.interfaces import TaxStrategy
from tax.infrastructure.strategies.brazilian import BrazilianTaxStrategy
from tax.infrastructure.strategies.eu_vat import EUVATStrategy
from tax.infrastructure.strategies.exempt import ExemptTaxStrategy
from tax.infrastructure.strategies.us_federal import USFederalTaxStrategy

_STRATEGY_MAP: dict[str, TaxStrategy] = {
    "brazil": BrazilianTaxStrategy(),
    "us": USFederalTaxStrategy(state_code="CA"),
    "eu": EUVATStrategy(),
    "exempt": ExemptTaxStrategy(),
}


def get_strategy(name: str) -> TaxStrategy:
    """Resolve a strategy by name.

    Raises:
        InvalidStrategyError: when name is not registered.
    """
    strategy = _STRATEGY_MAP.get(name.lower())
    if strategy is None:
        raise InvalidStrategyError(name)
    return strategy


def get_all_strategies() -> dict[str, TaxStrategy]:
    """Return all registered strategies."""
    return dict(_STRATEGY_MAP)


def resolve_strategy_for_customer(country: CustomerCountry) -> TaxStrategy:
    """Auto-select strategy based on customer country."""
    if country == CustomerCountry.BRAZIL:
        return BrazilianTaxStrategy()
    if country == CustomerCountry.USA:
        return USFederalTaxStrategy()
    if country in {
        CustomerCountry.GERMANY,
        CustomerCountry.FRANCE,
        CustomerCountry.PORTUGAL,
        CustomerCountry.ITALY,
        CustomerCountry.SPAIN,
        CustomerCountry.NETHERLANDS,
    }:
        return EUVATStrategy()
    return ExemptTaxStrategy()
