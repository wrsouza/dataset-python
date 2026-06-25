"""Application use cases for the product variant system.

Each use case has a single responsibility and depends on domain interfaces,
not on concrete Django models (DIP).
"""
from __future__ import annotations

from typing import Any

from products.domain.entities import VariantRecord
from products.domain.interfaces import Product, ProductRegistry
from products.infrastructure.models import ProductModel, ProductVariantModel


class ListTemplatesUseCase:
    """SRP: returns the list of registered product template keys."""

    def __init__(self, registry: ProductRegistry) -> None:
        self._registry = registry

    def execute(self) -> list[str]:
        return self._registry.list_templates()


class CloneProductUseCase:
    """Clones a product prototype and persists the variant to the database.

    Orchestrates: registry.clone() → persist to ProductVariantModel.
    SRP: only responsible for the clone-and-persist workflow.
    """

    def __init__(self, registry: ProductRegistry) -> None:
        self._registry = registry

    def execute(
        self,
        template_key: str,
        overrides: dict[str, Any],
        parent_db_id: int,
    ) -> VariantRecord:
        """Clone the template and persist the result.

        Args:
            template_key: Registry key for the template to clone.
            overrides: Attribute overrides for the new variant.
            parent_db_id: DB id of the parent ProductModel record.

        Returns:
            VariantRecord with the persisted data.
        """
        cloned: Product = self._registry.clone(template_key, overrides)
        parent = ProductModel.objects.get(pk=parent_db_id)

        variant = ProductVariantModel.objects.create(
            parent=parent,
            name=cloned.name,
            base_price=cloned.base_price,
            sku=cloned.get_sku(),
            extra_attrs=cloned.attributes,
        )
        return VariantRecord(
            id=variant.pk,
            parent_product_id=parent_db_id,
            sku=variant.sku,
            name=variant.name,
            base_price=float(variant.base_price),
            product_type=parent.product_type,
            extra_attrs=variant.extra_attrs,
        )


class ListVariantsUseCase:
    """SRP: lists all variants for a given product template."""

    def execute(self, product_id: int) -> list[VariantRecord]:
        variants = ProductVariantModel.objects.filter(parent_id=product_id)
        return [
            VariantRecord(
                id=v.pk,
                parent_product_id=product_id,
                sku=v.sku,
                name=v.name,
                base_price=float(v.base_price),
                product_type=v.parent.product_type,
                extra_attrs=v.extra_attrs,
            )
            for v in variants.select_related("parent")
        ]
