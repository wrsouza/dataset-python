"""Django ORM models for the products domain."""
from __future__ import annotations

from django.db import models


class ProductModel(models.Model):
    """Persisted product template record.

    Polymorphism is handled at the domain layer (Prototype pattern),
    not at the database layer — one table stores all product types with
    a JSON field for type-specific attributes (simple and performant for MySQL).
    """

    PRODUCT_TYPES = [
        ("physical", "Physical"),
        ("digital", "Digital"),
        ("subscription", "Subscription"),
    ]

    name = models.CharField(max_length=255)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, default="")
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES)
    sku = models.CharField(max_length=50, unique=True)
    extra_attrs = models.JSONField(default=dict)
    is_template = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.sku})"


class ProductVariantModel(models.Model):
    """A cloned variant derived from a product template."""

    parent = models.ForeignKey(
        ProductModel,
        on_delete=models.CASCADE,
        related_name="variants",
    )
    name = models.CharField(max_length=255)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    sku = models.CharField(max_length=50, unique=True)
    extra_attrs = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "product_variants"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Variant {self.name} of {self.parent.name}"


class ProductAttributeModel(models.Model):
    """Named attribute key-value pair for a product (display metadata)."""

    product = models.ForeignKey(
        ProductModel,
        on_delete=models.CASCADE,
        related_name="product_attributes",
    )
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=500)

    class Meta:
        db_table = "product_attributes"
        unique_together = [("product", "key")]

    def __str__(self) -> str:
        return f"{self.product.name}: {self.key}={self.value}"
