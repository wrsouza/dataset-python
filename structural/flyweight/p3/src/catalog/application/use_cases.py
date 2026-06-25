"""Application use cases — orchestrate the Flyweight factory and repository."""

from __future__ import annotations

from decimal import Decimal

from catalog.domain.entities import FlyweightStats, Product
from catalog.domain.interfaces import (
    ProductRepositoryProtocol,
    ProductTypeFactoryProtocol,
)


class NoProductTypesLoadedError(ValueError):
    def __init__(self) -> None:
        super().__init__(
            "Factory has no ProductType flyweights loaded — "
            "call load_all_from_definitions() first."
        )


class PopulateProductsUseCase:
    """Creates `count` products distributed round-robin across all ProductTypes.

    SRP: only responsible for generating and persisting products.
    DIP: depends on the factory/repository protocols, not concrete Django models.
    """

    def __init__(
        self,
        factory: ProductTypeFactoryProtocol,
        repository: ProductRepositoryProtocol,
    ) -> None:
        self._factory = factory
        self._repository = repository

    def execute(self, count: int) -> int:
        types = self._factory.get_all_types()
        if not types:
            raise NoProductTypesLoadedError

        products = [
            Product(
                name=f"{product_type.brand} {product_type.category_name} #{i}",
                price=Decimal("9.99") + Decimal(i % 200),
                sku=f"SKU-{i:07d}",
                stock=10 + i % 50,
                product_type=product_type,
            )
            for i, product_type in ((i, types[i % len(types)]) for i in range(count))
        ]
        self._repository.bulk_save(products)
        return len(products)


class GetFactoryStatsUseCase:
    """Computes Flyweight memory economy: unique types vs. total products."""

    def __init__(
        self,
        factory: ProductTypeFactoryProtocol,
        repository: ProductRepositoryProtocol,
    ) -> None:
        self._factory = factory
        self._repository = repository

    def execute(self) -> FlyweightStats:
        return FlyweightStats(
            unique_types=self._factory.cached_count(),
            total_products=self._repository.count(),
        )


class ListProductsUseCase:
    """Paginated product listing — repository handles the actual query."""

    def __init__(self, repository: ProductRepositoryProtocol) -> None:
        self._repository = repository

    def execute(self, page: int, page_size: int) -> list[Product]:
        return self._repository.list_paginated(page, page_size)
