"""Django ORM model for catalog products."""

from __future__ import annotations

from django.db import models


class ProductModel(models.Model):
    """Persistent representation of a Product."""

    objects: models.Manager[ProductModel]

    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100, db_index=True)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.name} ({self.category})"
