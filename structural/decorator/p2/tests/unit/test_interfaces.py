"""Unit tests for the DataService / DataServiceDecorator ABCs."""

from __future__ import annotations

from unittest.mock import MagicMock

from cache_decorator.domain.entities import DataQuery, DataResult
from cache_decorator.domain.interfaces import DataService, DataServiceDecorator


class _StubDecorator(DataServiceDecorator):
    """Minimal concrete decorator used only to exercise the default delegation."""


def test_decorator_default_delegates_to_wrapped(sample_query: DataQuery) -> None:
    wrapped = MagicMock(spec=DataService)
    expected = DataResult(
        product_id="sku-001", price=1.0, currency="USD", fetched_at="now"
    )
    wrapped.get_data.return_value = expected

    decorator = _StubDecorator(wrapped)
    result = decorator.get_data(sample_query)

    wrapped.get_data.assert_called_once_with(sample_query)
    assert result is expected


def test_decorator_is_a_data_service() -> None:
    wrapped = MagicMock(spec=DataService)
    decorator = _StubDecorator(wrapped)
    assert isinstance(decorator, DataService)
