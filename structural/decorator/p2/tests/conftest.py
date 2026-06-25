"""Shared fixtures for the Cache Decorator API test suite."""

from __future__ import annotations

from unittest.mock import MagicMock

import fakeredis
import pytest

from cache_decorator.domain.entities import DataQuery, DataResult


@pytest.fixture
def sample_query() -> DataQuery:
    return DataQuery(product_id="sku-001")


@pytest.fixture
def sample_result() -> DataResult:
    return DataResult(
        product_id="sku-001",
        price=19.90,
        currency="USD",
        fetched_at="2026-01-01T00:00:00+00:00",
    )


@pytest.fixture
def mock_wrapped() -> MagicMock:
    """A MagicMock standing in for a wrapped DataService."""
    return MagicMock()


@pytest.fixture
def fake_redis_client() -> fakeredis.FakeRedis:
    """An in-memory fake Redis client — no real server needed."""
    return fakeredis.FakeRedis(decode_responses=True)
