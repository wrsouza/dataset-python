"""Integration tests for the catalog_iterator Django views."""

from __future__ import annotations

import pytest
from django.test import Client

from catalog_iterator.infrastructure.models import ProductModel

pytestmark = pytest.mark.django_db


def _seed(count: int) -> None:
    ProductModel.objects.bulk_create(
        [
            ProductModel(name=f"p-{i}", price=10.0 * i, category="general")
            for i in range(1, count + 1)
        ]
    )


def test_product_list_returns_first_page(client: Client) -> None:
    _seed(5)

    response = client.get("/products/", {"limit": 2})

    body = response.json()
    assert len(body["items"]) == 2
    assert body["next_cursor"] is not None


def test_category_summary_aggregates_across_pages(client: Client) -> None:
    ProductModel.objects.bulk_create(
        [
            ProductModel(name="b1", price=10.0, category="books"),
            ProductModel(name="b2", price=20.0, category="books"),
            ProductModel(name="t1", price=5.0, category="toys"),
        ]
    )

    response = client.get("/products/category-summary/")

    body = {item["category"]: item for item in response.json()}
    assert body["books"]["product_count"] == 2
    assert body["toys"]["product_count"] == 1
