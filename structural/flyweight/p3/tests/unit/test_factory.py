"""Unit tests for ProductTypeFactory — verifies Flyweight sharing."""

from __future__ import annotations

from decimal import Decimal

from catalog.infrastructure.factory import ProductTypeFactory


def test_get_or_create_returns_same_instance_for_identical_state() -> None:
    factory = ProductTypeFactory()

    a = factory.get_or_create(
        "Electronics", "Sony", Decimal("18.00"), "heavy", "30 days"
    )
    b = factory.get_or_create(
        "Electronics", "Sony", Decimal("18.00"), "heavy", "30 days"
    )

    assert a is b


def test_get_or_create_returns_different_instance_for_different_brand() -> None:
    factory = ProductTypeFactory()

    sony = factory.get_or_create(
        "Electronics", "Sony", Decimal("18.00"), "heavy", "30 days"
    )
    lg = factory.get_or_create(
        "Electronics", "LG", Decimal("18.00"), "heavy", "30 days"
    )

    assert sony is not lg


def test_load_all_from_definitions_populates_around_50_types() -> None:
    factory = ProductTypeFactory()

    factory.load_all_from_definitions()

    assert factory.cached_count() == len(factory.get_definitions())
    assert factory.cached_count() >= 40


def test_load_all_from_definitions_is_idempotent() -> None:
    factory = ProductTypeFactory()
    factory.load_all_from_definitions()
    first_count = factory.cached_count()

    factory.load_all_from_definitions()

    assert factory.cached_count() == first_count


def test_get_all_types_reflects_cache() -> None:
    factory = ProductTypeFactory()
    factory.get_or_create("Books", "Penguin", Decimal("0.00"), "light", "no returns")

    types = factory.get_all_types()

    assert len(types) == 1
    assert types[0].brand == "Penguin"


def test_product_type_is_frozen() -> None:
    import dataclasses

    import pytest

    factory = ProductTypeFactory()
    product_type = factory.get_or_create(
        "Toys", "LEGO", Decimal("8.00"), "standard", "30 days"
    )

    with pytest.raises(dataclasses.FrozenInstanceError):
        product_type.brand = "Hacked"  # type: ignore[misc]
