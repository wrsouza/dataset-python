"""Unit tests for domain entities — pure Python, no Django/DB required."""

from __future__ import annotations

from decimal import Decimal

from catalog.domain.entities import FlyweightStats, Product, ProductType


def make_type(**overrides: object) -> ProductType:
    defaults: dict[str, object] = {
        "category_name": "Electronics",
        "brand": "Samsung",
        "tax_rate": Decimal("18.00"),
        "shipping_class": "heavy",
        "return_policy": "30 days",
    }
    defaults.update(overrides)
    return ProductType(**defaults)  # type: ignore[arg-type]


def test_product_type_calculates_tax_amount() -> None:
    product_type = make_type(tax_rate=Decimal("10.00"))

    assert product_type.calculate_tax_amount(Decimal("100.00")) == Decimal("10.00")


def test_product_type_key_is_stable_for_equal_state() -> None:
    a = make_type()
    b = make_type()

    assert a.type_key == b.type_key
    assert a == b


def test_product_delegates_category_and_brand_to_flyweight() -> None:
    product_type = make_type(category_name="Books", brand="Penguin")
    product = Product(
        name="Dune",
        price=Decimal("19.99"),
        sku="BK-1",
        stock=5,
        product_type=product_type,
    )

    assert product.category == "Books"
    assert product.brand == "Penguin"


def test_product_price_with_tax_uses_shared_flyweight_rate() -> None:
    product_type = make_type(tax_rate=Decimal("20.00"))
    product = Product(
        name="TV",
        price=Decimal("100.00"),
        sku="TV-1",
        stock=1,
        product_type=product_type,
    )

    assert product.tax_amount == Decimal("20.00")
    assert product.price_with_tax == Decimal("120.00")


def test_flyweight_stats_sharing_ratio() -> None:
    stats = FlyweightStats(unique_types=50, total_products=10000)

    assert stats.sharing_ratio == 200.0


def test_flyweight_stats_memory_savings_are_positive_at_scale() -> None:
    stats = FlyweightStats(unique_types=50, total_products=10000)

    assert stats.memory_saved_bytes > 0
    assert 0 < stats.savings_percentage <= 100


def test_flyweight_stats_zero_types_does_not_divide_by_zero() -> None:
    stats = FlyweightStats(unique_types=0, total_products=0)

    assert stats.sharing_ratio == 0.0
    assert stats.savings_percentage == 0.0
