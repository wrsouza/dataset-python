"""Leaf and Composite implementations of CatalogItem.

Product  → Leaf   (no children, holds concrete data)
Category → Composite (holds children: list[CatalogItem])

Both satisfy the CatalogItem contract — LSP is explicit here.
OCP: add Bundle/Kit as new CatalogItem subclass without touching
existing code.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from catalog.domain.interfaces import CatalogItem, ProductData

if TYPE_CHECKING:
    pass


class ProductLeaf(CatalogItem):
    """Leaf node — a single product with no children.

    Every method is self-contained and returns a valid, non-empty result,
    satisfying the same contract as CategoryComposite (LSP).
    """

    def __init__(
        self,
        name: str,
        price: Decimal,
        sku: str,
        stock_qty: int,
        category_id: int | None = None,
        product_id: int | None = None,
    ) -> None:
        self._name = name
        self._price = price
        self._sku = sku
        self._stock_qty = stock_qty
        self._category_id = category_id
        self._product_id = product_id

    # ── CatalogItem interface ─────────────────────────────────────────────────

    @property
    def name(self) -> str:
        return self._name

    def get_product_count(self) -> int:
        return 1

    def get_all_products(self) -> list[ProductData]:
        return [
            ProductData(
                name=self._name,
                price=self._price,
                sku=self._sku,
                stock_qty=self._stock_qty,
                category_id=self._category_id,
            )
        ]

    def calculate_total_value(self) -> Decimal:
        return self._price * Decimal(self._stock_qty)

    def to_dict(self, depth: int = 0) -> dict:  # type: ignore[type-arg]
        return {
            "type": "product",
            "id": self._product_id,
            "name": self._name,
            "sku": self._sku,
            "price": str(self._price),
            "stock_qty": self._stock_qty,
            "total_value": str(self.calculate_total_value()),
            "depth": depth,
        }


class CategoryComposite(CatalogItem):
    """Composite node — a category that contains other CatalogItems.

    Delegates all recursive operations to children, accumulating results.
    Children may be ProductLeafs or other CategoryComposites — both are
    treated uniformly via the CatalogItem interface.
    """

    def __init__(
        self,
        category_id: int,
        name: str,
        slug: str,
        parent_id: int | None = None,
    ) -> None:
        self._category_id = category_id
        self._name = name
        self._slug = slug
        self._parent_id = parent_id
        self._children: list[CatalogItem] = []

    # ── child management ──────────────────────────────────────────────────────

    def add_child(self, child: CatalogItem) -> None:
        self._children.append(child)

    def remove_child(self, child: CatalogItem) -> None:
        self._children.remove(child)

    def get_children(self) -> list[CatalogItem]:
        return list(self._children)

    @property
    def slug(self) -> str:
        return self._slug

    @property
    def name(self) -> str:
        return self._name

    # ── CatalogItem interface ─────────────────────────────────────────────────

    def get_product_count(self) -> int:
        return sum(child.get_product_count() for child in self._children)

    def get_all_products(self) -> list[ProductData]:
        products: list[ProductData] = []
        for child in self._children:
            products.extend(child.get_all_products())
        return products

    def calculate_total_value(self) -> Decimal:
        return sum(
            (child.calculate_total_value() for child in self._children),
            Decimal("0"),
        )

    def to_dict(self, depth: int = 0) -> dict:  # type: ignore[type-arg]
        return {
            "type": "category",
            "id": self._category_id,
            "name": self._name,
            "slug": self._slug,
            "parent_id": self._parent_id,
            "product_count": self.get_product_count(),
            "total_value": str(self.calculate_total_value()),
            "depth": depth,
            "children": [child.to_dict(depth + 1) for child in self._children],
        }
