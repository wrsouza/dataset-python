"""Django ORM models for the catalog app."""

from __future__ import annotations

from django.db import models


class ProductTypeModel(models.Model):
    """Persistent representation of the ProductType Flyweight data."""

    objects: models.Manager[ProductTypeModel]

    category_name = models.CharField(max_length=100, db_index=True)
    brand = models.CharField(max_length=100, db_index=True)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)
    shipping_class = models.CharField(max_length=50)
    return_policy = models.CharField(max_length=100)

    class Meta:
        app_label = "catalog"
        db_table = "catalog_product_type"
        unique_together = [("category_name", "brand", "shipping_class")]

    def __str__(self) -> str:
        return f"{self.brand} / {self.category_name}"


class ProductModel(models.Model):
    """Persistent representation of a Product context."""

    objects: models.Manager[ProductModel]

    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sku = models.CharField(max_length=50, unique=True, db_index=True)
    stock = models.IntegerField(default=0)
    product_type = models.ForeignKey(
        ProductTypeModel, on_delete=models.PROTECT, related_name="products"
    )

    class Meta:
        app_label = "catalog"
        db_table = "catalog_product"

    def __str__(self) -> str:
        return f"{self.sku} — {self.name}"
