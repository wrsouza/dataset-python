"""Integration tests for Flask routes using a real in-memory CacheManager."""

from __future__ import annotations

from typing import Any

import pytest

from cache.infrastructure.singleton import CacheManager


@pytest.fixture(autouse=True)
def reset_singleton() -> Any:
    CacheManager._instance = None
    yield
    CacheManager._instance = None


@pytest.fixture
def client() -> Any:
    import os
    import sys

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

    # Patch configure so it does not try to reach a real Redis
    from unittest.mock import patch

    with patch.object(CacheManager, "configure"):
        from main import app

        app.config["TESTING"] = True
        with app.test_client() as c:
            yield c


def test_products_endpoint_returns_list(client: Any) -> None:
    response = client.get("/products")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_products_second_request_is_cached(client: Any) -> None:
    client.get("/products")
    response = client.get("/products")
    assert response.headers.get("X-Cache") == "HIT"


def test_cache_stats_endpoint(client: Any) -> None:
    response = client.get("/cache/stats")
    assert response.status_code == 200
    data = response.get_json()
    assert "circuit_state" in data
    assert "singleton_id" in data


def test_cache_flush_endpoint(client: Any) -> None:
    client.get("/products")  # populate cache
    response = client.post("/cache/flush")
    assert response.status_code == 200
    data = response.get_json()
    assert data["flushed"] is True
