"""Unit tests for domain entities."""

from __future__ import annotations

from cache_proxy.domain.entities import CacheStats, StockData, WeatherData


def test_weather_data_fields() -> None:
    w = WeatherData(
        city="London",
        temperature_c=15.0,
        humidity_percent=80.0,
        description="Cloudy",
        wind_speed_kmh=20.0,
    )
    assert w.city == "London"
    assert w.temperature_c == 15.0


def test_stock_data_fields() -> None:
    s = StockData(
        ticker="AAPL",
        price_usd=178.5,
        change_percent=1.2,
        volume=5_000_000,
        market_cap_billions=2800.0,
    )
    assert s.ticker == "AAPL"
    assert s.price_usd == 178.5


def test_cache_stats_hit_rate_zero_when_empty() -> None:
    stats = CacheStats()
    assert stats.hit_rate == 0.0
    assert stats.total == 0


def test_cache_stats_hit_rate_calculation() -> None:
    stats = CacheStats(hits=3, misses=1)
    assert stats.total == 4
    assert stats.hit_rate == 0.75


def test_cache_stats_full_hit_rate() -> None:
    stats = CacheStats(hits=10, misses=0)
    assert stats.hit_rate == 1.0
