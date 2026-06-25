"""Unit tests for product prototypes.

Key assertion: modifying a clone must NOT affect the original template.
"""
from __future__ import annotations

import pytest

from products.infrastructure.prototypes import (
    DigitalProduct,
    PhysicalProduct,
    ProductTemplateRegistry,
    SubscriptionProduct,
    build_default_registry,
)


class TestPhysicalProductClone:
    """Tests for PhysicalProduct clone independence."""

    def test_clone_is_different_object(self) -> None:
        product = PhysicalProduct(
            name="Tênis Running",
            base_price=299.90,
            description="Tênis para corrida.",
            weight_kg=0.5,
            dimensions_cm={"width": 30.0, "height": 12.0, "depth": 20.0},
        )
        clone = product.clone({})
        assert clone is not product

    def test_clone_sku_differs_from_original(self) -> None:
        """Each clone must get a fresh unique SKU."""
        product = PhysicalProduct(
            name="Tênis",
            base_price=299.90,
            description="",
            weight_kg=0.5,
            dimensions_cm={"width": 30.0, "height": 12.0, "depth": 20.0},
        )
        clone = product.clone({})
        assert clone.get_sku() != product.get_sku()

    def test_clone_dimensions_are_independent(self) -> None:
        """Mutating dimensions on the clone must not affect the original."""
        product = PhysicalProduct(
            name="Caixa",
            base_price=10.0,
            description="",
            weight_kg=1.0,
            dimensions_cm={"width": 10.0, "height": 10.0, "depth": 10.0},
        )
        clone = product.clone({})
        # Mutate via attributes dict
        clone.attributes["dimensions_cm"]["width"] = 999.0
        assert product.dimensions_cm["width"] == 10.0

    def test_clone_applies_price_override(self) -> None:
        product = PhysicalProduct(
            name="Camiseta",
            base_price=49.90,
            description="",
            weight_kg=0.2,
            dimensions_cm={"width": 50.0, "height": 70.0, "depth": 1.0},
        )
        clone = product.clone({"base_price": 59.90})
        assert clone.base_price == pytest.approx(59.90)
        assert product.base_price == pytest.approx(49.90)

    def test_clone_applies_name_override(self) -> None:
        product = PhysicalProduct(
            name="Camiseta P",
            base_price=49.90,
            description="",
            weight_kg=0.2,
            dimensions_cm={"width": 50.0, "height": 70.0, "depth": 1.0},
        )
        clone = product.clone({"name": "Camiseta GG"})
        assert clone.name == "Camiseta GG"
        assert product.name == "Camiseta P"


class TestDigitalProductClone:
    """Tests for DigitalProduct clone independence."""

    def test_clone_has_independent_attributes(self) -> None:
        product = DigitalProduct(
            name="Curso Python",
            base_price=199.90,
            description="Curso completo de Python.",
            download_url="https://cdn.example.com/curso-python.zip",
            file_size_mb=500.0,
        )
        clone = product.clone({"download_url": "https://cdn.example.com/v2.zip"})
        assert clone.download_url == "https://cdn.example.com/v2.zip"
        assert product.download_url == "https://cdn.example.com/curso-python.zip"

    def test_multiple_clones_independent(self) -> None:
        product = DigitalProduct(
            name="E-book",
            base_price=29.90,
            description="",
            download_url="https://cdn.example.com/ebook.pdf",
            file_size_mb=5.0,
        )
        clone_a = product.clone({"name": "E-book Edição A"})
        clone_b = product.clone({"name": "E-book Edição B"})
        assert clone_a.name == "E-book Edição A"
        assert clone_b.name == "E-book Edição B"
        assert product.name == "E-book"


class TestSubscriptionProductClone:
    """Tests for SubscriptionProduct clone independence."""

    def test_clone_billing_cycle_override(self) -> None:
        product = SubscriptionProduct(
            name="Pro Plan",
            base_price=99.90,
            description="Plano Pro.",
            billing_cycle="monthly",
            trial_days=7,
        )
        clone = product.clone({"billing_cycle": "annual"})
        assert clone.billing_cycle == "annual"
        assert product.billing_cycle == "monthly"

    def test_original_trial_days_unchanged(self) -> None:
        product = SubscriptionProduct(
            name="Enterprise",
            base_price=499.90,
            description="",
            billing_cycle="annual",
            trial_days=30,
        )
        clone = product.clone({"trial_days": 60})
        assert clone.trial_days == 60
        assert product.trial_days == 30


class TestProductTemplateRegistry:
    """Tests for the PrototypeRegistry."""

    def test_register_and_get(self) -> None:
        registry = ProductTemplateRegistry()
        product = PhysicalProduct(
            name="Item",
            base_price=10.0,
            description="",
            weight_kg=0.1,
            dimensions_cm={"width": 5.0, "height": 5.0, "depth": 5.0},
        )
        registry.register("item-key", product)
        retrieved = registry.get("item-key")
        assert retrieved is product

    def test_get_unknown_key_raises(self) -> None:
        from products.domain.entities import ProductNotFoundError

        registry = ProductTemplateRegistry()
        with pytest.raises(ProductNotFoundError):
            registry.get("nonexistent")

    def test_clone_returns_new_object(self) -> None:
        registry = ProductTemplateRegistry()
        product = DigitalProduct(
            name="PDF",
            base_price=9.90,
            description="",
            download_url="https://example.com/file.pdf",
            file_size_mb=2.0,
        )
        registry.register("pdf", product)
        clone = registry.clone("pdf", {"name": "PDF Premium"})
        assert clone is not product
        assert clone.name == "PDF Premium"
        assert product.name == "PDF"

    def test_list_templates(self) -> None:
        registry = build_default_registry()
        templates = registry.list_templates()
        assert "tshirt-basic" in templates
        assert "ebook-python" in templates
        assert "saas-starter" in templates

    def test_registry_clone_does_not_mutate_original(self) -> None:
        registry = build_default_registry()
        original_price = registry.get("tshirt-basic").base_price
        registry.clone("tshirt-basic", {"base_price": 999.0})
        assert registry.get("tshirt-basic").base_price == pytest.approx(original_price)

    def test_product_type_specific_attributes_preserved(self) -> None:
        """LSP: clones must preserve subclass-specific attributes."""
        product = SubscriptionProduct(
            name="Starter",
            base_price=49.90,
            description="",
            billing_cycle="monthly",
            trial_days=14,
        )
        registry = ProductTemplateRegistry()
        registry.register("starter", product)
        clone = registry.clone("starter", {})
        # Subclass-specific attributes must survive the clone
        assert "billing_cycle" in clone.attributes
        assert "trial_days" in clone.attributes
