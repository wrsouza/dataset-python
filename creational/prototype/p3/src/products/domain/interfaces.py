"""Domain interfaces for the Product Prototype pattern.

Defines the Prototype ABC and ProductRegistry interface.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Product(ABC):
    """Prototype interface for e-commerce products.

    All product types must implement clone() to support creating variant
    copies without depending on concrete classes (OCP).
    """

    @abstractmethod
    def clone(self, variant_attrs: dict[str, Any]) -> Product:
        """Create a deep copy of this product with variant overrides applied.

        Args:
            variant_attrs: Attributes to override in the new variant.

        Returns:
            A new Product instance independent from this original.
        """
        ...

    @abstractmethod
    def get_sku(self) -> str:
        """Return the unique SKU for this product."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Product name."""
        ...

    @property
    @abstractmethod
    def base_price(self) -> float:
        """Base price in BRL."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Product description."""
        ...

    @property
    @abstractmethod
    def attributes(self) -> dict[str, Any]:
        """Product-type-specific attributes."""
        ...

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for API responses."""
        ...


class ProductRegistry(ABC):
    """Registry interface for managing product prototypes.

    Follows OCP: new product templates are registered without modifying this interface.
    """

    @abstractmethod
    def register(self, key: str, product: Product) -> None:
        """Register a product template under the given key."""
        ...

    @abstractmethod
    def get(self, key: str) -> Product:
        """Retrieve a registered product template by key."""
        ...

    @abstractmethod
    def clone(self, key: str, overrides: dict[str, Any]) -> Product:
        """Clone a registered product template and apply overrides."""
        ...

    @abstractmethod
    def list_templates(self) -> list[str]:
        """Return all registered template keys."""
        ...
