"""Unit tests for the 4 mock API clients — deterministic, no network calls."""

from __future__ import annotations

from aggregator.infrastructure.crypto_client import MockCryptoAPIClient
from aggregator.infrastructure.news_client import MockNewsAPIClient
from aggregator.infrastructure.stock_client import MockStockAPIClient
from aggregator.infrastructure.weather_client import MockWeatherAPIClient


def test_weather_client_is_deterministic() -> None:
    client = MockWeatherAPIClient()

    first = client.get_weather("London")
    second = client.get_weather("London")

    assert first == second
    assert first.city == "London"


def test_weather_client_differs_per_city() -> None:
    client = MockWeatherAPIClient()

    london = client.get_weather("London")
    tokyo = client.get_weather("Tokyo")

    assert london != tokyo


def test_stock_client_is_deterministic() -> None:
    client = MockStockAPIClient()

    first = client.get_quote("AAPL")
    second = client.get_quote("AAPL")

    assert first == second
    assert first.ticker == "AAPL"
    assert first.price > 0


def test_crypto_client_is_deterministic() -> None:
    client = MockCryptoAPIClient()

    first = client.get_quote("BTC")
    second = client.get_quote("BTC")

    assert first == second
    assert first.symbol == "BTC"
    assert first.price_usd > 0


def test_news_client_returns_requested_limit() -> None:
    client = MockNewsAPIClient()

    items = client.get_latest("markets", limit=3)

    assert len(items) == 3
    assert all(item.title.startswith("Markets") for item in items)
