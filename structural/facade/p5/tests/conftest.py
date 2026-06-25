"""Shared fixtures for Multi-API Aggregator Facade tests."""

from __future__ import annotations

import pytest

from aggregator.application.facade import DataAggregatorFacade
from aggregator.infrastructure.cache_manager import InMemoryCacheManager
from aggregator.infrastructure.crypto_client import MockCryptoAPIClient
from aggregator.infrastructure.news_client import MockNewsAPIClient
from aggregator.infrastructure.stock_client import MockStockAPIClient
from aggregator.infrastructure.weather_client import MockWeatherAPIClient


@pytest.fixture
def facade() -> DataAggregatorFacade:
    return DataAggregatorFacade(
        weather_client=MockWeatherAPIClient(),
        stock_client=MockStockAPIClient(),
        crypto_client=MockCryptoAPIClient(),
        news_client=MockNewsAPIClient(),
        cache=InMemoryCacheManager(),
    )
