"""Integration tests for the UI Component Factory Flask API.

These tests run against the real Flask app (with a real PostgreSQL connection).
Run via: docker-compose run --rm app pytest tests/integration/ -v
"""
from __future__ import annotations

import os

import pytest


# Skip integration tests when PostgreSQL is not available
pytestmark = pytest.mark.skipif(
    os.environ.get("DATABASE_URL") is None,
    reason="DATABASE_URL not set — skipping integration tests",
)


@pytest.fixture
def client():  # type: ignore[no-untyped-def]
    """Flask test client with the real app."""
    from ui_factory.app import app

    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_health_endpoint(client) -> None:  # type: ignore[no-untyped-def]
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"


@pytest.mark.parametrize("platform", ["windows", "linux", "mac"])
def test_get_components_returns_200(client, platform: str) -> None:  # type: ignore[no-untyped-def]
    response = client.get(f"/components/{platform}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["platform"] == platform
    assert "components" in data
    assert all(k in data["components"] for k in ("button", "input", "modal"))


def test_get_components_unsupported_platform_returns_400(client) -> None:  # type: ignore[no-untyped-def]
    response = client.get("/components/dos")
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_logs_endpoint_returns_list(client) -> None:  # type: ignore[no-untyped-def]
    # First generate some usage
    client.get("/components/windows")
    response = client.get("/logs")
    assert response.status_code == 200
    data = response.get_json()
    assert "logs" in data
    assert isinstance(data["logs"], list)


def test_components_persist_to_database(client) -> None:  # type: ignore[no-untyped-def]
    """Verify that API calls are logged in PostgreSQL."""
    client.get("/components/linux")
    logs_response = client.get("/logs")
    logs = logs_response.get_json()["logs"]
    platforms = [log["platform"] for log in logs]
    assert "linux" in platforms
