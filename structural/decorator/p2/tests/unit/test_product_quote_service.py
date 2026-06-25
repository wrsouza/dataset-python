"""Unit tests for the ConcreteComponent: ProductQuoteService."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from cache_decorator.domain.entities import DataQuery, DataResult
from cache_decorator.domain.exceptions import ProductNotFoundError
from cache_decorator.domain.interfaces import DataService
from cache_decorator.infrastructure.product_quote_service import ProductQuoteService


@pytest.fixture
def service() -> ProductQuoteService:
    return ProductQuoteService()


def test_service_satisfies_data_service(service: ProductQuoteService) -> None:
    assert isinstance(service, DataService)


def test_get_data_returns_result_for_known_product(
    service: ProductQuoteService,
) -> None:
    with patch("cache_decorator.infrastructure.product_quote_service.time.sleep"):
        result = service.get_data(DataQuery(product_id="sku-001"))

    assert isinstance(result, DataResult)
    assert result.product_id == "sku-001"
    assert result.price == 19.90
    assert result.currency == "USD"
    assert result.fetched_at


def test_get_data_is_case_insensitive(service: ProductQuoteService) -> None:
    with patch("cache_decorator.infrastructure.product_quote_service.time.sleep"):
        result = service.get_data(DataQuery(product_id="SKU-002"))

    assert result.price == 149.00


def test_get_data_raises_for_unknown_product(service: ProductQuoteService) -> None:
    with patch("cache_decorator.infrastructure.product_quote_service.time.sleep"):
        with pytest.raises(ProductNotFoundError):
            service.get_data(DataQuery(product_id="does-not-exist"))
