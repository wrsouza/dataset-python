"""Unit tests for use cases — factory/repository mocked (DIP in action)."""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from catalog.application.use_cases import (
    GetFactoryStatsUseCase,
    ListProductsUseCase,
    NoProductTypesLoadedError,
    PopulateProductsUseCase,
)
from catalog.domain.entities import FlyweightStats, Product, ProductType


def _make_type(brand: str) -> ProductType:
    return ProductType(
        category_name="Electronics",
        brand=brand,
        tax_rate=Decimal("18.00"),
        shipping_class="heavy",
        return_policy="30 days",
    )


def test_populate_products_distributes_round_robin_across_types() -> None:
    factory = MagicMock()
    factory.get_all_types.return_value = [_make_type("A"), _make_type("B")]
    repository = MagicMock()

    use_case = PopulateProductsUseCase(factory=factory, repository=repository)
    created = use_case.execute(count=5)

    assert created == 5
    saved_products: list[Product] = repository.bulk_save.call_args[0][0]
    assert len(saved_products) == 5
    assert saved_products[0].product_type.brand == "A"
    assert saved_products[1].product_type.brand == "B"


def test_populate_products_raises_when_no_types_loaded() -> None:
    factory = MagicMock()
    factory.get_all_types.return_value = []
    repository = MagicMock()

    use_case = PopulateProductsUseCase(factory=factory, repository=repository)

    with pytest.raises(NoProductTypesLoadedError):
        use_case.execute(count=10)


def test_get_factory_stats_combines_factory_and_repository() -> None:
    factory = MagicMock()
    factory.cached_count.return_value = 50
    repository = MagicMock()
    repository.count.return_value = 10000

    use_case = GetFactoryStatsUseCase(factory=factory, repository=repository)
    stats = use_case.execute()

    assert stats == FlyweightStats(unique_types=50, total_products=10000)


def test_list_products_delegates_to_repository() -> None:
    repository = MagicMock()
    expected = [
        Product(
            name="Item",
            price=Decimal("9.99"),
            sku="SKU-1",
            stock=5,
            product_type=_make_type("A"),
        )
    ]
    repository.list_paginated.return_value = expected

    use_case = ListProductsUseCase(repository=repository)
    result = use_case.execute(page=2, page_size=10)

    assert result == expected
    repository.list_paginated.assert_called_once_with(2, 10)
