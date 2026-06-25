"""Integration tests for DjangoProductRepository against a real ORM."""

from __future__ import annotations

import pytest

from catalog_iterator.infrastructure.models import ProductModel
from catalog_iterator.infrastructure.repository import DjangoProductRepository

pytestmark = pytest.mark.django_db


def _seed(count: int) -> None:
    ProductModel.objects.bulk_create(
        [
            ProductModel(name=f"p-{i}", price=10.0 * i, category="general")
            for i in range(1, count + 1)
        ]
    )


def test_fetch_chunk_returns_next_cursor_when_full_page() -> None:
    _seed(5)
    repository = DjangoProductRepository()

    products, next_cursor = repository.fetch_chunk(None, limit=2)

    assert len(products) == 2
    assert next_cursor is not None


def test_fetch_chunk_returns_none_cursor_on_last_partial_page() -> None:
    _seed(3)
    repository = DjangoProductRepository()

    first_page, cursor = repository.fetch_chunk(None, limit=2)
    second_page, next_cursor = repository.fetch_chunk(cursor, limit=2)

    assert len(first_page) == 2
    assert len(second_page) == 1
    assert next_cursor is None


def test_fetch_chunk_returns_empty_for_empty_catalog() -> None:
    repository = DjangoProductRepository()

    products, next_cursor = repository.fetch_chunk(None, limit=10)

    assert products == []
    assert next_cursor is None
