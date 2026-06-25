"""Concrete Prototype implementations for e-commerce products.

Each class is a ConcretePrototype that knows how to clone itself.
LSP is satisfied: all subtypes are substitutable for Product without
any client code needing to know the concrete type.
"""
from __future__ import annotations

import copy
import uuid
from typing import Any

from products.domain.entities import ProductNotFoundError
from products.domain.interfaces import Product, ProductRegistry


class BaseProduct(Product):
    """Base implementation shared by all concrete product prototypes.

    Uses copy.deepcopy to ensure the clone is completely independent
    from the original — nested dicts and lists are new objects.
    """

    def __init__(
        self,
        name: str,
        base_price: float,
        description: str,
        sku_prefix: str,
        extra_attrs: dict[str, Any] | None = None,
    ) -> None:
        self._name = name
        self._base_price = base_price
        self._description = description
        self._sku_prefix = sku_prefix
        # Generate unique SKU on construction; clone overrides via variant_attrs
        self._sku = f"{sku_prefix}-{uuid.uuid4().hex[:8].upper()}"
        self._extra_attrs: dict[str, Any] = extra_attrs or {}

    @property
    def name(self) -> str:
        return self._name

    @property
    def base_price(self) -> float:
        return self._base_price

    @property
    def description(self) -> str:
        return self._description

    @property
    def attributes(self) -> dict[str, Any]:
        return dict(self._extra_attrs)

    def get_sku(self) -> str:
        return self._sku

    def clone(self, variant_attrs: dict[str, Any]) -> BaseProduct:
        """Deep clone this product and apply variant overrides.

        copy.deepcopy ensures nested structures (dicts, lists) in extra_attrs
        are independent copies, not shared references.
        """
        cloned = copy.deepcopy(self)
        # Assign a fresh SKU for the new variant
        cloned._sku = f"{cloned._sku_prefix}-{uuid.uuid4().hex[:8].upper()}"
        cloned._apply_variant_attrs(variant_attrs)
        return cloned

    def _apply_variant_attrs(self, attrs: dict[str, Any]) -> None:
        """Apply variant overrides to this (cloned) product instance."""
        if "name" in attrs:
            self._name = str(attrs["name"])
        if "base_price" in attrs:
            self._base_price = float(attrs["base_price"])
        if "description" in attrs:
            self._description = str(attrs["description"])
        # Merge extra_attrs so subclass-specific fields can be overridden
        for key, value in attrs.items():
            if key not in {"name", "base_price", "description"}:
                self._extra_attrs[key] = value

    def to_dict(self) -> dict[str, Any]:
        return {
            "sku": self._sku,
            "name": self._name,
            "base_price": self._base_price,
            "description": self._description,
            "product_type": self.__class__.__name__,
            "attributes": self.attributes,
        }


class PhysicalProduct(BaseProduct):
    """ConcretePrototype for physical goods.

    Adds weight (kg) and dimensions (cm) on top of base product.
    LSP: substitutable for Product — clone() honours the same contract.
    """

    def __init__(
        self,
        name: str,
        base_price: float,
        description: str,
        weight_kg: float,
        dimensions_cm: dict[str, float],
    ) -> None:
        super().__init__(
            name=name,
            base_price=base_price,
            description=description,
            sku_prefix="PHYS",
            extra_attrs={
                "weight_kg": weight_kg,
                "dimensions_cm": dict(dimensions_cm),
            },
        )

    @property
    def weight_kg(self) -> float:
        return float(self._extra_attrs["weight_kg"])

    @property
    def dimensions_cm(self) -> dict[str, float]:
        return dict(self._extra_attrs["dimensions_cm"])


class DigitalProduct(BaseProduct):
    """ConcretePrototype for downloadable digital goods.

    Adds download_url and file_size_mb.
    LSP: clone() always returns a fully independent DigitalProduct.
    """

    def __init__(
        self,
        name: str,
        base_price: float,
        description: str,
        download_url: str,
        file_size_mb: float,
    ) -> None:
        super().__init__(
            name=name,
            base_price=base_price,
            description=description,
            sku_prefix="DGTL",
            extra_attrs={
                "download_url": download_url,
                "file_size_mb": file_size_mb,
            },
        )

    @property
    def download_url(self) -> str:
        return str(self._extra_attrs["download_url"])

    @property
    def file_size_mb(self) -> float:
        return float(self._extra_attrs["file_size_mb"])


class SubscriptionProduct(BaseProduct):
    """ConcretePrototype for recurring subscription products.

    Adds billing_cycle (monthly/annual) and trial_days.
    """

    def __init__(
        self,
        name: str,
        base_price: float,
        description: str,
        billing_cycle: str,
        trial_days: int,
    ) -> None:
        super().__init__(
            name=name,
            base_price=base_price,
            description=description,
            sku_prefix="SUBS",
            extra_attrs={
                "billing_cycle": billing_cycle,
                "trial_days": trial_days,
            },
        )

    @property
    def billing_cycle(self) -> str:
        return str(self._extra_attrs["billing_cycle"])

    @property
    def trial_days(self) -> int:
        return int(self._extra_attrs["trial_days"])


class ProductTemplateRegistry(ProductRegistry):
    """Concrete PrototypeRegistry managing product templates.

    SRP: only responsible for storing and cloning product templates.
    OCP: new product types are registered without modifying this class.
    """

    def __init__(self) -> None:
        self._templates: dict[str, Product] = {}

    def register(self, key: str, product: Product) -> None:
        """Register a product template under the given key."""
        self._templates[key] = product

    def get(self, key: str) -> Product:
        """Retrieve a registered template by key."""
        if key not in self._templates:
            raise ProductNotFoundError(key)
        return self._templates[key]

    def clone(self, key: str, overrides: dict[str, Any]) -> Product:
        """Clone a template and apply variant overrides.

        Sequence:
        1. Retrieve template from registry.
        2. Call clone() — uses copy.deepcopy internally.
        3. Overrides are already applied inside clone().
        """
        template = self.get(key)
        return template.clone(overrides)

    def list_templates(self) -> list[str]:
        """Return all registered template keys."""
        return list(self._templates.keys())


def build_default_registry() -> ProductTemplateRegistry:
    """Factory that builds and populates the default product registry.

    Composition root: the only place that knows about concrete product types.
    """
    registry = ProductTemplateRegistry()

    registry.register(
        "tshirt-basic",
        PhysicalProduct(
            name="Camiseta Básica",
            base_price=49.90,
            description="Camiseta 100% algodão, corte regular.",
            weight_kg=0.2,
            dimensions_cm={"width": 50.0, "height": 70.0, "depth": 1.0},
        ),
    )
    registry.register(
        "ebook-python",
        DigitalProduct(
            name="E-book Python Avançado",
            base_price=79.90,
            description="E-book com 300 páginas sobre Python avançado.",
            download_url="https://cdn.example.com/ebooks/python-avancado.pdf",
            file_size_mb=12.5,
        ),
    )
    registry.register(
        "saas-starter",
        SubscriptionProduct(
            name="SaaS Starter Plan",
            base_price=99.90,
            description="Plano inicial com até 5 usuários.",
            billing_cycle="monthly",
            trial_days=14,
        ),
    )
    return registry
