"""Unit tests for RetryDecorator — wrapped service is fully mocked."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from cache_decorator.domain.entities import DataQuery, DataResult
from cache_decorator.infrastructure.retry_decorator import RetryDecorator


def test_returns_result_on_first_success(
    mock_wrapped: MagicMock, sample_query: DataQuery, sample_result: DataResult
) -> None:
    mock_wrapped.get_data.return_value = sample_result
    decorator = RetryDecorator(mock_wrapped, max_attempts=3, backoff_seconds=0)

    result = decorator.get_data(sample_query)

    assert result == sample_result
    mock_wrapped.get_data.assert_called_once_with(sample_query)


def test_retries_until_success(
    mock_wrapped: MagicMock, sample_query: DataQuery, sample_result: DataResult
) -> None:
    mock_wrapped.get_data.side_effect = [
        RuntimeError("transient"),
        RuntimeError("transient"),
        sample_result,
    ]
    decorator = RetryDecorator(mock_wrapped, max_attempts=3, backoff_seconds=0)

    with patch("cache_decorator.infrastructure.retry_decorator.time.sleep"):
        result = decorator.get_data(sample_query)

    assert result == sample_result
    assert mock_wrapped.get_data.call_count == 3


def test_raises_last_error_after_exhausting_attempts(
    mock_wrapped: MagicMock, sample_query: DataQuery
) -> None:
    mock_wrapped.get_data.side_effect = RuntimeError("persistent failure")
    decorator = RetryDecorator(mock_wrapped, max_attempts=2, backoff_seconds=0)

    with patch("cache_decorator.infrastructure.retry_decorator.time.sleep"):
        with pytest.raises(RuntimeError, match="persistent failure"):
            decorator.get_data(sample_query)

    assert mock_wrapped.get_data.call_count == 2


def test_backoff_sleeps_between_attempts(
    mock_wrapped: MagicMock, sample_query: DataQuery, sample_result: DataResult
) -> None:
    mock_wrapped.get_data.side_effect = [RuntimeError("once"), sample_result]
    decorator = RetryDecorator(mock_wrapped, max_attempts=2, backoff_seconds=0.5)

    with patch("cache_decorator.infrastructure.retry_decorator.time.sleep") as sleep:
        decorator.get_data(sample_query)

    sleep.assert_called_once_with(0.5 * 1)
