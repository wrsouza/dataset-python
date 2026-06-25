"""Unit tests for GetProductQuoteUseCase — DataService is fully mocked (DIP)."""

from __future__ import annotations

from unittest.mock import MagicMock

from cache_decorator.application.use_cases import GetProductQuoteUseCase
from cache_decorator.domain.entities import DataQuery, DataResult


def test_execute_builds_query_and_delegates(
    mock_wrapped: MagicMock, sample_result: DataResult
) -> None:
    mock_wrapped.get_data.return_value = sample_result
    use_case = GetProductQuoteUseCase(mock_wrapped)

    result = use_case.execute("sku-001")

    mock_wrapped.get_data.assert_called_once_with(DataQuery(product_id="sku-001"))
    assert result == sample_result
