"""Integration tests for the Flask app — fakeredis injected, no real Redis."""

from __future__ import annotations

from unittest.mock import patch

import fakeredis
import pytest
from flask.testing import FlaskClient

from cache_decorator.app import create_app


@pytest.fixture
def client() -> FlaskClient:
    fake_redis_client = fakeredis.FakeRedis(decode_responses=True)
    app = create_app(redis_client=fake_redis_client)
    app.testing = True
    return app.test_client()


def test_health_endpoint(client: FlaskClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_get_quote_for_known_product_returns_200(client: FlaskClient) -> None:
    with patch("cache_decorator.infrastructure.product_quote_service.time.sleep"):
        response = client.get("/quotes/sku-001")

    assert response.status_code == 200
    body = response.get_json()
    assert body["product_id"] == "sku-001"
    assert body["price"] == 19.90
    assert body["currency"] == "USD"


def test_get_quote_for_unknown_product_returns_404(client: FlaskClient) -> None:
    with patch("cache_decorator.infrastructure.product_quote_service.time.sleep"):
        response = client.get("/quotes/does-not-exist")

    assert response.status_code == 404
    assert "error" in response.get_json()


def test_second_call_is_served_from_cache(client: FlaskClient) -> None:
    """First call is a cache miss; second call for the same product is a hit."""
    with patch(
        "cache_decorator.infrastructure.product_quote_service.time.sleep"
    ) as sleep:
        first = client.get("/quotes/sku-002")
        second = client.get("/quotes/sku-002")

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.get_json() == second.get_json()
    # time.sleep only runs inside the real service — a cache hit on the
    # second call means the service body executes just once.
    assert sleep.call_count == 1
