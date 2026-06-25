"""Unit tests for the strategy registry: lookup, listing, and auto-resolution."""

from __future__ import annotations

import pytest

from tax.domain.entities import CustomerCountry
from tax.domain.exceptions import InvalidStrategyError
from tax.infrastructure.strategies.brazilian import BrazilianTaxStrategy
from tax.infrastructure.strategies.eu_vat import EUVATStrategy
from tax.infrastructure.strategies.exempt import ExemptTaxStrategy
from tax.infrastructure.strategies.registry import (
    get_all_strategies,
    get_strategy,
    resolve_strategy_for_customer,
)
from tax.infrastructure.strategies.us_federal import USFederalTaxStrategy


@pytest.mark.parametrize(
    ("key", "expected_type"),
    [
        ("brazil", BrazilianTaxStrategy),
        ("us", USFederalTaxStrategy),
        ("eu", EUVATStrategy),
        ("exempt", ExemptTaxStrategy),
    ],
)
def test_get_strategy_resolves_known_keys(key: str, expected_type: type) -> None:
    assert isinstance(get_strategy(key), expected_type)


def test_get_strategy_is_case_insensitive() -> None:
    assert isinstance(get_strategy("BRAZIL"), BrazilianTaxStrategy)


def test_get_strategy_raises_for_unknown_key() -> None:
    with pytest.raises(InvalidStrategyError):
        get_strategy("mars")


def test_get_all_strategies_returns_every_registered_strategy() -> None:
    strategies = get_all_strategies()

    assert set(strategies.keys()) == {"brazil", "us", "eu", "exempt"}


def test_get_all_strategies_returns_a_copy() -> None:
    strategies = get_all_strategies()
    strategies["custom"] = ExemptTaxStrategy()

    assert "custom" not in get_all_strategies()


@pytest.mark.parametrize(
    ("country", "expected_type"),
    [
        (CustomerCountry.BRAZIL, BrazilianTaxStrategy),
        (CustomerCountry.USA, USFederalTaxStrategy),
        (CustomerCountry.GERMANY, EUVATStrategy),
        (CustomerCountry.OTHER, ExemptTaxStrategy),
    ],
)
def test_resolve_strategy_for_customer_maps_country_to_strategy(
    country: CustomerCountry, expected_type: type
) -> None:
    assert isinstance(resolve_strategy_for_customer(country), expected_type)
