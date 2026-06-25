"""Integration tests for catalog Django views using SQLite in-memory DB."""

from __future__ import annotations

import json

# Django must be configured before importing models.
import os
from decimal import Decimal

import django
from django.test import Client, TestCase

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings_test")
django.setup()

from catalog.models import Category, Product  # noqa: E402


class CategoryViewTests(TestCase):
    """Integration tests that hit the real Django ORM and views."""

    def setUp(self) -> None:
        self.client = Client()
        # L1
        self.electronics = Category.objects.create(
            name="Electronics", slug="electronics"
        )
        # L2
        self.smartphones = Category.objects.create(
            name="Smartphones", slug="smartphones", parent=self.electronics
        )
        # L3
        self.android = Category.objects.create(
            name="Android", slug="android", parent=self.smartphones
        )
        # Products at L3
        self.p1 = Product.objects.create(
            name="Pixel 8",
            sku="PIX-8",
            price=Decimal("699.99"),
            stock_qty=10,
            category=self.android,
        )
        self.p2 = Product.objects.create(
            name="Galaxy S24",
            sku="SAM-S24",
            price=Decimal("999.99"),
            stock_qty=5,
            category=self.android,
        )

    def test_category_list_returns_200(self) -> None:
        resp = self.client.get("/categories/")
        assert resp.status_code == 200

    def test_category_list_contains_root(self) -> None:
        resp = self.client.get("/categories/")
        data = json.loads(resp.content)
        slugs = [item["slug"] for item in data]
        assert "electronics" in slugs

    def test_category_detail_returns_subtree(self) -> None:
        resp = self.client.get("/categories/electronics/")
        assert resp.status_code == 200
        data = json.loads(resp.content)
        assert data["slug"] == "electronics"
        assert data["product_count"] == 2

    def test_category_products_returns_flat_list(self) -> None:
        resp = self.client.get("/categories/electronics/products/")
        assert resp.status_code == 200
        data = json.loads(resp.content)
        assert data["total"] == 2
        skus = {p["sku"] for p in data["products"]}
        assert skus == {"PIX-8", "SAM-S24"}

    def test_category_stats_returns_counts_and_value(self) -> None:
        resp = self.client.get("/categories/electronics/stats/")
        assert resp.status_code == 200
        data = json.loads(resp.content)
        assert data["product_count"] == 2
        # (699.99 * 10) + (999.99 * 5) = 6999.90 + 4999.95 = 11999.85
        assert Decimal(data["total_value"]) == Decimal("6999.90") + Decimal("4999.95")

    def test_android_subtree_products(self) -> None:
        resp = self.client.get("/categories/android/products/")
        data = json.loads(resp.content)
        assert data["total"] == 2

    def test_unknown_slug_raises_404(self) -> None:
        resp = self.client.get("/categories/nonexistent-slug-xyz/")
        assert resp.status_code == 404
