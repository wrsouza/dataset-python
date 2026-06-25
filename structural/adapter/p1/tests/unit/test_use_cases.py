"""Unit tests for application use cases.

Use cases depend on RESTProductService (Protocol), so we can inject
any duck-typed fake without touching infrastructure.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from soap_adapter.application.use_cases import (
    CreateProductUseCase,
    GetProductUseCase,
    ListProductsUseCase,
)
from soap_adapter.domain.entities import Product, ProductCreate


def _make_product(**kwargs: object) -> Product:
    defaults = {
        "id": "1",
        "name": "Sample",
        "price": 10.0,
        "category": "General",
        "stock": 50,
    }
    defaults.update(kwargs)
    return Product(**defaults)  # type: ignore[arg-type]


class TestGetProductUseCase:
    def test_delegates_to_service(self) -> None:
        service = MagicMock()
        service.get_product.return_value = _make_product(id="99")
        use_case = GetProductUseCase(service=service)

        result = use_case.execute("99")

        service.get_product.assert_called_once_with("99")
        assert result.id == "99"


class TestListProductsUseCase:
    def test_returns_all_products(self) -> None:
        service = MagicMock()
        service.list_products.return_value = [_make_product(), _make_product(id="2")]
        use_case = ListProductsUseCase(service=service)

        result = use_case.execute()

        assert len(result) == 2


class TestCreateProductUseCase:
    def test_passes_data_to_service(self) -> None:
        service = MagicMock()
        created = _make_product(id="new")
        service.create_product.return_value = created
        use_case = CreateProductUseCase(service=service)
        data = ProductCreate(name="New", price=1.0, category="X", stock=1)

        result = use_case.execute(data)

        service.create_product.assert_called_once_with(data)
        assert result.id == "new"
