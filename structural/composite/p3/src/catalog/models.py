"""Django ORM models for the catalog domain.

Adjacency list pattern for Category (self-referential FK).
"""

from __future__ import annotations

from django.db import models


class Category(models.Model):
    """Composite node persisted in MySQL via adjacency list."""

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
    )

    class Meta:
        db_table = "categories"
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    """Leaf node — a product belonging to a category."""

    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sku = models.CharField(max_length=100, unique=True)
    stock_qty = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="products",
    )

    class Meta:
        db_table = "products"
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.sku} — {self.name}"
