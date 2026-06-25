"""Core entities for the lazy product catalog domain."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Product:
    """A single product — the element type this Iterator traverses."""

    product_id: int
    name: str
    price: float
    category: str


@dataclass(frozen=True)
class ProductsPage:
    """One page of products plus the cursor to fetch the next page, if any."""

    items: list[Product]
    next_cursor: str | None


@dataclass(frozen=True)
class CategorySummary:
    """Aggregate statistics for a single category, computed by iterating."""

    category: str
    product_count: int
    total_price: float
