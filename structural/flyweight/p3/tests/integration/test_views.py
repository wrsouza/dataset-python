"""Integration tests for catalog Django views using SQLite in-memory DB."""

from __future__ import annotations

import json
import os
from decimal import Decimal

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings_test")
django.setup()

from django.test import Client, TestCase  # noqa: E402

from catalog.domain.entities import Product  # noqa: E402
from catalog.infrastructure.factory import ProductTypeFactory  # noqa: E402
from catalog.infrastructure.repository import DjangoProductRepository  # noqa: E402


class ProductViewTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        factory = ProductTypeFactory()
        factory.load_all_from_definitions()
        repository = DjangoProductRepository(factory=factory)
        product_type = factory.get_all_types()[0]
        repository.bulk_save(
            [
                Product(
                    name=f"Item {i}",
                    price=Decimal("9.99"),
                    sku=f"SKU-VIEW-{i:03d}",
                    stock=5,
                    product_type=product_type,
                )
                for i in range(15)
            ]
        )

    def test_product_list_returns_paginated_products(self) -> None:
        response = self.client.get("/products/?page=1&page_size=10")

        assert response.status_code == 200
        body = json.loads(response.content)
        assert len(body["products"]) == 10
        assert body["page"] == 1

    def test_product_list_second_page_has_remaining_products(self) -> None:
        response = self.client.get("/products/?page=2&page_size=10")

        body = json.loads(response.content)
        assert len(body["products"]) == 5

    def test_products_share_same_flyweight_id(self) -> None:
        response = self.client.get("/products/?page=1&page_size=15")

        body = json.loads(response.content)
        flyweight_ids = {p["flyweight_id"] for p in body["products"]}
        assert len(flyweight_ids) == 1  # all 15 share one ProductType

    def test_factory_stats_reports_sharing_ratio(self) -> None:
        response = self.client.get("/products/stats/")

        assert response.status_code == 200
        body = json.loads(response.content)
        assert body["total_products"] == 15
        assert "memory" in body
        assert "savings_percentage" in body["memory"]
