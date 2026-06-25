"""Domain interfaces — DIP boundary for P3 catalog."""

from __future__ import annotations

from typing import Protocol

from catalog.domain.entities import Product, ProductType


class ProductTypeFactoryProtocol(Protocol):
    """FlyweightFactory protocol for ProductType objects."""

    def get_or_create(
        self,
        category_name: str,
        brand: str,
        tax_rate: object,
        shipping_class: str,
        return_policy: str,
    ) -> ProductType: ...

    def cached_count(self) -> int: ...

    def get_all_types(self) -> list[ProductType]: ...


class ProductRepositoryProtocol(Protocol):
    """Repository protocol for Product contexts."""

    def save(self, product: Product) -> None: ...

    def bulk_save(self, products: list[Product]) -> None: ...

    def count(self) -> int: ...

    def list_paginated(self, page: int, page_size: int) -> list[Product]: ...
