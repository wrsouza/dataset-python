"""Integration tests for Django views.

Uses Django's test client with an in-memory SQLite database
(overridden in conftest.py) so no MySQL container is required for tests.
"""
from __future__ import annotations

import json

import pytest
from django.test import Client


@pytest.mark.django_db
class TestProductTemplatesView:
    def test_returns_templates_list(self) -> None:
        client = Client()
        response = client.get("/products/templates/")
        assert response.status_code == 200
        data = json.loads(response.content)
        assert "templates" in data
        assert isinstance(data["templates"], list)
        assert len(data["templates"]) > 0


@pytest.mark.django_db
class TestCloneProductView:
    def test_clone_nonexistent_product_returns_404(self) -> None:
        client = Client()
        response = client.post(
            "/products/clone/9999/",
            data=json.dumps({"overrides": {}}),
            content_type="application/json",
        )
        assert response.status_code == 404

    def test_clone_creates_variant(self) -> None:
        from products.infrastructure.models import ProductModel

        parent = ProductModel.objects.create(
            name="Camiseta Template",
            base_price=49.90,
            description="Template",
            product_type="physical",
            sku="PHYS-TEMPLATE-001",
            is_template=True,
        )

        client = Client()
        response = client.post(
            f"/products/clone/{parent.pk}/",
            data=json.dumps({"overrides": {"name": "Camiseta GG", "base_price": 59.90}}),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = json.loads(response.content)
        assert data["name"] == "Camiseta GG"
        assert data["base_price"] == pytest.approx(59.90)
        assert data["parent_product_id"] == parent.pk


@pytest.mark.django_db
class TestProductVariantsView:
    def test_variants_nonexistent_product_returns_404(self) -> None:
        client = Client()
        response = client.get("/products/9999/variants/")
        assert response.status_code == 404

    def test_variants_empty_list(self) -> None:
        from products.infrastructure.models import ProductModel

        product = ProductModel.objects.create(
            name="Produto Teste",
            base_price=10.0,
            description="",
            product_type="digital",
            sku="DGTL-TEST-001",
        )
        client = Client()
        response = client.get(f"/products/{product.pk}/variants/")
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["variants"] == []
