"""Integration tests for DjangoProductRepository — real ORM, SQLite in-memory."""

from __future__ import annotations

import os
from decimal import Decimal

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings_test")
django.setup()

from django.test import TestCase  # noqa: E402

from catalog.domain.entities import Product  # noqa: E402
from catalog.infrastructure.factory import ProductTypeFactory  # noqa: E402
from catalog.infrastructure.repository import DjangoProductRepository  # noqa: E402


class DjangoProductRepositoryTests(TestCase):
    def setUp(self) -> None:
        self.factory = ProductTypeFactory()
        self.factory.load_all_from_definitions()
        self.repository = DjangoProductRepository(factory=self.factory)

    def test_save_persists_a_single_product(self) -> None:
        product_type = self.factory.get_all_types()[0]
        product = Product(
            name="Test Item",
            price=Decimal("19.99"),
            sku="SKU-SAVE-1",
            stock=10,
            product_type=product_type,
        )

        self.repository.save(product)

        assert self.repository.count() == 1

    def test_bulk_save_reuses_the_same_type_model_for_shared_flyweight(self) -> None:
        product_type = self.factory.get_all_types()[0]
        products = [
            Product(
                name=f"Item {i}",
                price=Decimal("9.99"),
                sku=f"SKU-BULK-{i}",
                stock=1,
                product_type=product_type,
            )
            for i in range(20)
        ]

        self.repository.bulk_save(products)

        from catalog.models import ProductTypeModel

        assert self.repository.count() == 20
        assert ProductTypeModel.objects.count() == 1  # one shared type row

    def test_list_paginated_returns_correct_page(self) -> None:
        product_type = self.factory.get_all_types()[0]
        products = [
            Product(
                name=f"Item {i}",
                price=Decimal("9.99"),
                sku=f"SKU-PAGE-{i:03d}",
                stock=1,
                product_type=product_type,
            )
            for i in range(25)
        ]
        self.repository.bulk_save(products)

        page_1 = self.repository.list_paginated(page=1, page_size=10)
        page_2 = self.repository.list_paginated(page=2, page_size=10)

        assert len(page_1) == 10
        assert len(page_2) == 10
        assert {p.sku for p in page_1} != {p.sku for p in page_2}

    def test_to_domain_reconstructs_product_with_factory_flyweight(self) -> None:
        product_type = self.factory.get_all_types()[0]
        self.repository.save(
            Product(
                name="Reconstructed",
                price=Decimal("5.00"),
                sku="SKU-RECON-1",
                stock=3,
                product_type=product_type,
            )
        )

        results = self.repository.list_paginated(page=1, page_size=1)

        assert results[0].product_type.brand == product_type.brand
