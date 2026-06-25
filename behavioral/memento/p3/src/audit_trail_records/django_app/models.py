"""Django ORM models used to persist products and their audit trail."""

from __future__ import annotations

from django.db import models


class ProductModel(models.Model):
    """Current (latest) state of a product."""

    objects: models.Manager[ProductModel]

    product_id = models.CharField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    price = models.FloatField()
    stock = models.IntegerField()
    current_version = models.IntegerField(default=1)

    def __str__(self) -> str:
        return f"{self.product_id} (v{self.current_version})"


class AuditRecordModel(models.Model):
    """Persisted snapshot (memento) of a ProductModel at a given version."""

    objects: models.Manager[AuditRecordModel]

    product_id = models.CharField(max_length=64, db_index=True)
    version = models.IntegerField()
    name = models.CharField(max_length=200)
    price = models.FloatField()
    stock = models.IntegerField()
    changed_by = models.CharField(max_length=100)
    created_at = models.DateTimeField()

    class Meta:
        ordering = ["product_id", "version"]
        unique_together = [("product_id", "version")]

    def __str__(self) -> str:
        return f"{self.product_id} v{self.version} ({self.changed_by})"
