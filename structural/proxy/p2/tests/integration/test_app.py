"""Integration tests for the Flask app — real RedisCacheProxy, fakeredis backend.

create_app() builds a real redis.Redis client at call time; monkeypatching
redis.Redis to return a fakeredis instance before calling create_app() lets
the full HTTP -> use case -> RedisCacheProxy -> MockExternalAPIService flow
run for real without a live Redis server.
"""

from __future__ import annotations

from collections.abc import Iterator
from unittest.mock import patch

import fakeredis
import pytest
from flask.testing import FlaskClient

import cache_proxy.main as main_module


@pytest.fixture
def client() -> Iterator[FlaskClient]:
    fake_client = fakeredis.FakeStrictRedis(decode_responses=True)
    with (
        patch.object(main_module.redis, "Redis", return_value=fake_client),
        patch("cache_proxy.infrastructure.real_subject._simulate_latency"),
    ):
        app = main_module.create_app()
        app.testing = True
        with app.test_client() as test_client:
            yield test_client


def test_weather_endpoint_returns_data(client: FlaskClient) -> None:
    response = client.get("/weather/London")

    assert response.status_code == 200
    body = response.get_json()
    assert body["city"] == "London"


def test_weather_endpoint_is_cached_on_second_call(client: FlaskClient) -> None:
    first = client.get("/weather/Paris").get_json()
    second = client.get("/weather/Paris").get_json()

    assert first == second

    stats = client.get("/cache/stats").get_json()
    assert stats["hits"] == 1
    assert stats["misses"] == 1


def test_exchange_endpoint_returns_rate(client: FlaskClient) -> None:
    response = client.get("/exchange/usd/eur")

    assert response.status_code == 200
    body = response.get_json()
    assert body["from"] == "USD"
    assert body["to"] == "EUR"
    assert isinstance(body["rate"], float)


def test_stocks_endpoint_returns_data(client: FlaskClient) -> None:
    response = client.get("/stocks/AAPL")

    assert response.status_code == 200
    body = response.get_json()
    assert body["ticker"] == "AAPL"


def test_cache_stats_endpoint_reports_hit_rate(client: FlaskClient) -> None:
    client.get("/stocks/MSFT")
    client.get("/stocks/MSFT")

    response = client.get("/cache/stats")

    assert response.status_code == 200
    body = response.get_json()
    assert body["total"] == 2
    assert body["hit_rate"] == 0.5


def test_cache_flush_removes_keys(client: FlaskClient) -> None:
    client.get("/weather/Tokyo")

    response = client.delete("/cache/flush")

    assert response.status_code == 200
    assert response.get_json()["keys_removed"] >= 1

    stats_before_refetch = client.get("/cache/stats").get_json()
    client.get("/weather/Tokyo")
    stats_after_refetch = client.get("/cache/stats").get_json()
    assert stats_after_refetch["misses"] > stats_before_refetch["misses"]
