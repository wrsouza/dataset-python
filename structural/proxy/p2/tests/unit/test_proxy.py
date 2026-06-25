"""Unit tests for RedisCacheProxy — all Redis calls are mocked."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from cache_proxy.domain.entities import StockData, WeatherData
from cache_proxy.domain.interfaces import ExternalAPIService
from cache_proxy.infrastructure.proxy import RedisCacheProxy
from cache_proxy.infrastructure.real_subject import MockExternalAPIService

# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def mock_redis() -> MagicMock:
    r = MagicMock()
    r.get.return_value = None  # default: cache miss
    r.setex.return_value = True
    r.keys.return_value = []
    r.delete.return_value = 0
    return r


@pytest.fixture
def real_subject() -> MockExternalAPIService:
    svc = MockExternalAPIService()
    # Override latency for tests
    with patch("cache_proxy.infrastructure.real_subject._simulate_latency"):
        yield svc


@pytest.fixture
def proxy(
    real_subject: MockExternalAPIService, mock_redis: MagicMock
) -> RedisCacheProxy:
    return RedisCacheProxy(wrapped=real_subject, redis_client=mock_redis)


# ── LSP: Proxy satisfies ExternalAPIService Protocol ────────────────────────


def test_proxy_satisfies_external_api_service_protocol(proxy: RedisCacheProxy) -> None:
    """Proxy must be substitutable for ExternalAPIService (LSP)."""
    assert isinstance(proxy, ExternalAPIService)


def test_real_subject_satisfies_external_api_service_protocol() -> None:
    """RealSubject must also satisfy the ExternalAPIService Protocol (LSP)."""
    svc = MockExternalAPIService()
    assert isinstance(svc, ExternalAPIService)


# ── Cache MISS → delegates to real subject ────────────────────────────────


def test_get_weather_cache_miss_calls_real_subject(
    proxy: RedisCacheProxy, mock_redis: MagicMock
) -> None:
    with patch("cache_proxy.infrastructure.real_subject._simulate_latency"):
        result = proxy.get_weather("Paris")
    assert isinstance(result, WeatherData)
    assert result.city == "Paris"
    mock_redis.setex.assert_called_once()
    assert proxy.get_stats().misses == 1
    assert proxy.get_stats().hits == 0


def test_get_stock_cache_miss_calls_real_subject(
    proxy: RedisCacheProxy, mock_redis: MagicMock
) -> None:
    with patch("cache_proxy.infrastructure.real_subject._simulate_latency"):
        result = proxy.get_stock_price("AAPL")
    assert isinstance(result, StockData)
    assert result.ticker == "AAPL"
    assert proxy.get_stats().misses == 1


def test_get_exchange_rate_cache_miss_calls_real_subject(
    proxy: RedisCacheProxy, mock_redis: MagicMock
) -> None:
    with patch("cache_proxy.infrastructure.real_subject._simulate_latency"):
        rate = proxy.get_exchange_rate("USD", "EUR")
    assert isinstance(rate, float)
    assert rate > 0
    assert proxy.get_stats().misses == 1


# ── Cache HIT → does NOT call real subject ────────────────────────────────


def test_get_weather_cache_hit_returns_cached(
    proxy: RedisCacheProxy, mock_redis: MagicMock
) -> None:
    cached_weather = WeatherData(
        city="Tokyo",
        temperature_c=22.0,
        humidity_percent=65.0,
        description="Clear sky",
        wind_speed_kmh=10.0,
    )
    mock_redis.get.return_value = json.dumps(cached_weather.__dict__)

    result = proxy.get_weather("Tokyo")

    assert result.city == "Tokyo"
    assert result.temperature_c == 22.0
    assert proxy.get_stats().hits == 1
    assert proxy.get_stats().misses == 0


def test_get_exchange_rate_cache_hit(
    proxy: RedisCacheProxy, mock_redis: MagicMock
) -> None:
    mock_redis.get.return_value = json.dumps({"rate": 0.92})

    rate = proxy.get_exchange_rate("USD", "EUR")

    assert rate == 0.92
    assert proxy.get_stats().hits == 1


def test_get_stock_cache_hit(proxy: RedisCacheProxy, mock_redis: MagicMock) -> None:
    cached_stock = StockData(
        ticker="MSFT",
        price_usd=378.9,
        change_percent=0.5,
        volume=3_000_000,
        market_cap_billions=2500.0,
    )
    mock_redis.get.return_value = json.dumps(cached_stock.__dict__)

    result = proxy.get_stock_price("MSFT")

    assert result.ticker == "MSFT"
    assert proxy.get_stats().hits == 1


# ── Statistics ────────────────────────────────────────────────────────────


def test_cache_stats_accumulate_across_calls(
    proxy: RedisCacheProxy, mock_redis: MagicMock
) -> None:
    """After 1 miss then 1 hit, hit_rate should be 0.5."""
    with patch("cache_proxy.infrastructure.real_subject._simulate_latency"):
        proxy.get_weather("Berlin")  # miss

    cached = WeatherData(
        city="Berlin",
        temperature_c=10.0,
        humidity_percent=70.0,
        description="Cloudy",
        wind_speed_kmh=15.0,
    )
    mock_redis.get.return_value = json.dumps(cached.__dict__)
    proxy.get_weather("Berlin")  # hit

    stats = proxy.get_stats()
    assert stats.hits == 1
    assert stats.misses == 1
    assert stats.hit_rate == 0.5


# ── Flush ─────────────────────────────────────────────────────────────────


def test_flush_calls_redis_delete(
    proxy: RedisCacheProxy, mock_redis: MagicMock
) -> None:
    mock_redis.keys.side_effect = [
        ["weather:paris"],
        ["exchange:USD:EUR"],
        ["stock:AAPL"],
    ]
    mock_redis.delete.return_value = 3

    removed = proxy.flush()

    assert removed == 3
    mock_redis.delete.assert_called_once()


def test_flush_raises_cache_backend_error_on_redis_failure(
    proxy: RedisCacheProxy, mock_redis: MagicMock
) -> None:
    import redis

    from cache_proxy.domain.exceptions import CacheBackendError

    mock_redis.keys.side_effect = redis.RedisError("connection lost")

    with pytest.raises(CacheBackendError):
        proxy.flush()


def test_get_cached_raises_cache_backend_error_on_redis_failure(
    proxy: RedisCacheProxy, mock_redis: MagicMock
) -> None:
    import redis

    from cache_proxy.domain.exceptions import CacheBackendError

    mock_redis.get.side_effect = redis.RedisError("connection lost")

    with pytest.raises(CacheBackendError):
        proxy.get_weather("London")


def test_set_cached_failure_is_non_fatal(
    proxy: RedisCacheProxy, mock_redis: MagicMock, real_subject: MockExternalAPIService
) -> None:
    import redis

    mock_redis.setex.side_effect = redis.RedisError("write failed")

    # Cache write failures must not bubble up to the caller.
    result = proxy.get_weather("Paris")

    assert result.city == "Paris"
