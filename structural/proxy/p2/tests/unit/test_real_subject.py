"""Unit tests for MockExternalAPIService (RealSubject)."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from cache_proxy.domain.entities import StockData, WeatherData
from cache_proxy.domain.interfaces import ExternalAPIService
from cache_proxy.infrastructure.real_subject import MockExternalAPIService


@pytest.fixture
def service() -> MockExternalAPIService:
    return MockExternalAPIService()


def test_real_subject_satisfies_protocol(service: MockExternalAPIService) -> None:
    assert isinstance(service, ExternalAPIService)


def test_get_weather_returns_weather_data(service: MockExternalAPIService) -> None:
    with patch("cache_proxy.infrastructure.real_subject._simulate_latency"):
        result = service.get_weather("Sydney")
    assert isinstance(result, WeatherData)
    assert result.city == "Sydney"
    assert -50.0 <= result.temperature_c <= 60.0
    assert 0.0 <= result.humidity_percent <= 100.0


def test_get_exchange_rate_returns_positive_float(
    service: MockExternalAPIService,
) -> None:
    with patch("cache_proxy.infrastructure.real_subject._simulate_latency"):
        rate = service.get_exchange_rate("USD", "EUR")
    assert isinstance(rate, float)
    assert rate > 0


def test_get_exchange_rate_same_currency_is_near_one(
    service: MockExternalAPIService,
) -> None:
    with patch("cache_proxy.infrastructure.real_subject._simulate_latency"):
        rate = service.get_exchange_rate("USD", "USD")
    assert 0.99 <= rate <= 1.01


def test_get_stock_price_returns_stock_data(service: MockExternalAPIService) -> None:
    with patch("cache_proxy.infrastructure.real_subject._simulate_latency"):
        result = service.get_stock_price("AAPL")
    assert isinstance(result, StockData)
    assert result.ticker == "AAPL"
    assert result.price_usd > 0
    assert result.volume > 0


def test_get_stock_price_unknown_ticker_uses_default(
    service: MockExternalAPIService,
) -> None:
    with patch("cache_proxy.infrastructure.real_subject._simulate_latency"):
        result = service.get_stock_price("ZZZZ")
    assert result.ticker == "ZZZZ"
    assert result.price_usd > 0
