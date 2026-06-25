"""Unit tests for LoggingDecorator — wrapped service is fully mocked."""

from __future__ import annotations

import logging
from unittest.mock import MagicMock

import pytest

from cache_decorator.domain.entities import DataQuery, DataResult
from cache_decorator.infrastructure.logging_decorator import LoggingDecorator


def test_logging_decorator_delegates_and_returns_result(
    mock_wrapped: MagicMock, sample_query: DataQuery, sample_result: DataResult
) -> None:
    mock_wrapped.get_data.return_value = sample_result
    decorator = LoggingDecorator(mock_wrapped)

    result = decorator.get_data(sample_query)

    mock_wrapped.get_data.assert_called_once_with(sample_query)
    assert result == sample_result


def test_logging_decorator_logs_success(
    mock_wrapped: MagicMock,
    sample_query: DataQuery,
    sample_result: DataResult,
    caplog: pytest.LogCaptureFixture,
) -> None:
    mock_wrapped.get_data.return_value = sample_result
    decorator = LoggingDecorator(mock_wrapped)

    with caplog.at_level(logging.INFO):
        decorator.get_data(sample_query)

    assert any("started" in message for message in caplog.messages)
    assert any("finished" in message for message in caplog.messages)


def test_logging_decorator_logs_and_reraises_on_failure(
    mock_wrapped: MagicMock,
    sample_query: DataQuery,
    caplog: pytest.LogCaptureFixture,
) -> None:
    mock_wrapped.get_data.side_effect = RuntimeError("boom")
    decorator = LoggingDecorator(mock_wrapped)

    with caplog.at_level(logging.INFO), pytest.raises(RuntimeError, match="boom"):
        decorator.get_data(sample_query)

    assert any("failed" in message for message in caplog.messages)
