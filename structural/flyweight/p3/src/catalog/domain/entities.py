"""Domain entities for Product Catalog — Flyweight pattern.

ProductType is the Flyweight: frozen dataclass sharing intrinsic state
(category, brand, tax, shipping class) across thousands of Product contexts.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ProductType:
    """Flyweight — intrinsic state shared by all products of the same type.

    frozen=True enforces immutability: ~50 ProductType instances can be shared
    by 10,000 Product instances, eliminating massive data duplication.
    category_name, brand, tax_rate, shipping_class and return_policy are
    identical for all products of the same type.
    """

    category_name: str
    brand: str
    tax_rate: Decimal
    shipping_class: str
    return_policy: str

    def __repr__(self) -> str:
        return (
            f"ProductType(category={self.category_name!r}, "
            f"brand={self.brand!r}, tax={self.tax_rate}%)"
        )

    @property
    def type_key(self) -> str:
        """Stable string key for this ProductType — used as dict key in factory."""
        return (
            f"{self.category_name}|{self.brand}|{self.tax_rate}|{self.shipping_class}"
        )

    def calculate_tax_amount(self, price: Decimal) -> Decimal:
        """Calculate tax amount from intrinsic tax_rate."""
        return (price * self.tax_rate / Decimal("100")).quantize(Decimal("0.01"))


@dataclass
class Product:
    """Context — combines extrinsic state with a shared ProductType Flyweight.

    name, price, sku and stock vary per product.
    product_type is the shared Flyweight — same object for all products of
    the same category/brand/tax combination.
    """

    name: str
    price: Decimal
    sku: str
    stock: int
    product_type: ProductType  # shared Flyweight reference

    @property
    def category(self) -> str:
        """Delegate to shared Flyweight."""
        return self.product_type.category_name

    @property
    def brand(self) -> str:
        """Delegate to shared Flyweight."""
        return self.product_type.brand

    @property
    def tax_amount(self) -> Decimal:
        """Calculate tax using shared Flyweight logic + extrinsic price."""
        return self.product_type.calculate_tax_amount(self.price)

    @property
    def price_with_tax(self) -> Decimal:
        return self.price + self.tax_amount

    def __repr__(self) -> str:
        return f"Product(sku={self.sku!r}, name={self.name!r}, price={self.price})"


@dataclass(frozen=True)
class FlyweightStats:
    """Statistics showing memory economy from the Flyweight pattern."""

    unique_types: int
    total_products: int

    @property
    def sharing_ratio(self) -> float:
        if self.unique_types == 0:
            return 0.0
        return self.total_products / self.unique_types

    @property
    def estimated_bytes_without_flyweight(self) -> int:
        """Assume ~500 bytes of duplicated ProductType data per product."""
        return self.total_products * 500

    @property
    def estimated_bytes_with_flyweight(self) -> int:
        """unique_types * 500 bytes + total_products * 8 bytes (pointer)."""
        return self.unique_types * 500 + self.total_products * 8

    @property
    def memory_saved_bytes(self) -> int:
        return max(
            0,
            self.estimated_bytes_without_flyweight
            - self.estimated_bytes_with_flyweight,
        )

    @property
    def savings_percentage(self) -> float:
        if self.estimated_bytes_without_flyweight == 0:
            return 0.0
        return self.memory_saved_bytes / self.estimated_bytes_without_flyweight * 100
