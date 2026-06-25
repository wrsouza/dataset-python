"""Component ABC for the Composite pattern — CatalogItem hierarchy.

Defines the uniform interface that both Leaf (Product) and
Composite (Category) implement, enabling recursive tree operations
without isinstance() checks in client code.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal


class CatalogItem(ABC):
    """Abstract Component: uniform interface for Products and Categories.

    LSP guarantee: every concrete subclass fulfils this full contract
    so callers can treat a single Product and an entire Category tree
    identically.

    OCP: adding new node types (e.g. Bundle, Kit) requires only a new
    subclass — no changes here or in the client views.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Display name of this node."""
        ...

    @abstractmethod
    def get_product_count(self) -> int:
        """Return the total number of leaf products under this node."""
        ...

    @abstractmethod
    def get_all_products(self) -> list[ProductData]:
        """Return a flat list of every product reachable from this node."""
        ...

    @abstractmethod
    def calculate_total_value(self) -> Decimal:
        """Return sum of (price × stock_qty) for all reachable products."""
        ...

    @abstractmethod
    def to_dict(self, depth: int = 0) -> dict:  # type: ignore[type-arg]
        """Serialise this node to a nested dict for API responses."""
        ...


class ProductData:
    """Value object — carries product data across layer boundaries."""

    __slots__ = ("name", "price", "sku", "stock_qty", "category_id")

    def __init__(
        self,
        name: str,
        price: Decimal,
        sku: str,
        stock_qty: int,
        category_id: int | None,
    ) -> None:
        self.name = name
        self.price = price
        self.sku = sku
        self.stock_qty = stock_qty
        self.category_id = category_id

    def __repr__(self) -> str:
        return f"ProductData(sku={self.sku!r}, name={self.name!r})"
