"""Domain entities for the product variant system."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CloneRequest:
    """Request data for cloning a product template."""

    product_id: int
    variant_attrs: dict[str, Any] = field(default_factory=dict)


@dataclass
class VariantRecord:
    """Persisted product variant record."""

    id: int
    parent_product_id: int
    sku: str
    name: str
    base_price: float
    product_type: str
    extra_attrs: dict[str, Any] = field(default_factory=dict)


class ProductNotFoundError(Exception):
    """Raised when a product template is not found."""

    def __init__(self, key: str) -> None:
        self.key = key
        super().__init__(f"Product template '{key}' not found in registry")


class VariantNotFoundError(Exception):
    """Raised when a product variant is not found."""

    def __init__(self, variant_id: int) -> None:
        self.variant_id = variant_id
        super().__init__(f"Variant with id={variant_id} not found")
