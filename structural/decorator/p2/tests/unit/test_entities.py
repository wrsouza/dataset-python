"""Unit tests for domain entities."""

from __future__ import annotations

import pytest

from cache_decorator.domain.entities import DataQuery, DataResult


def test_data_query_cache_key_is_lowercased() -> None:
    query = DataQuery(product_id="SKU-001")
    assert query.cache_key() == "quote:sku-001"


def test_data_query_is_frozen() -> None:
    query = DataQuery(product_id="sku-001")
    with pytest.raises(AttributeError):
        query.product_id = "sku-002"  # type: ignore[misc]


def test_data_result_is_frozen() -> None:
    result = DataResult(
        product_id="sku-001", price=1.0, currency="USD", fetched_at="now"
    )
    with pytest.raises(AttributeError):
        result.price = 2.0  # type: ignore[misc]


def test_data_result_holds_expected_fields() -> None:
    result = DataResult(
        product_id="sku-001", price=19.9, currency="USD", fetched_at="now"
    )
    assert result.product_id == "sku-001"
    assert result.price == 19.9
    assert result.currency == "USD"
    assert result.fetched_at == "now"
