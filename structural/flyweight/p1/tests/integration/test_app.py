"""Integration tests for the FastAPI app using TestClient + dependency overrides."""

from __future__ import annotations

from collections.abc import Iterator

import fakeredis
import pytest
from fastapi.testclient import TestClient

import main as main_module


@pytest.fixture
def client() -> Iterator[TestClient]:
    fake_client = fakeredis.FakeStrictRedis(server=fakeredis.FakeServer())
    main_module.app.dependency_overrides[main_module.get_redis] = lambda: fake_client
    with TestClient(main_module.app) as test_client:
        yield test_client
    main_module.app.dependency_overrides.clear()


def test_login_creates_session(client: TestClient) -> None:
    response = client.post("/auth/login", json={"user_id": "u1", "role": "admin"})

    assert response.status_code == 201
    body = response.json()
    assert body["user_id"] == "u1"
    assert body["role"] == "admin"
    assert "flyweight_id" in body


def test_two_logins_same_role_share_flyweight_id(client: TestClient) -> None:
    first = client.post("/auth/login", json={"user_id": "u1", "role": "viewer"})
    second = client.post("/auth/login", json={"user_id": "u2", "role": "viewer"})

    assert first.json()["flyweight_id"] == second.json()["flyweight_id"]


def test_get_session_returns_existing_session(client: TestClient) -> None:
    login_response = client.post(
        "/auth/login", json={"user_id": "u1", "role": "editor"}
    )
    token = login_response.json()["token"]

    response = client.get(f"/auth/session/{token}")

    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "u1"
    assert body["role"] == "editor"


def test_get_session_missing_token_returns_404(client: TestClient) -> None:
    response = client.get("/auth/session/does-not-exist")

    assert response.status_code == 404


def test_cache_stats_reflects_sharing(client: TestClient) -> None:
    client.post("/auth/login", json={"user_id": "u1", "role": "admin"})
    client.post("/auth/login", json={"user_id": "u2", "role": "admin"})

    response = client.get("/cache/stats")

    assert response.status_code == 200
    body = response.json()
    assert body["total_sessions"] == 2
    assert body["unique_flyweights"] == 1


def test_bulk_login_demo(client: TestClient) -> None:
    response = client.post(
        "/demo/bulk-login",
        json={"count": 20, "roles": ["admin", "viewer", "editor"]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["sessions_created"] == 20
    assert body["flyweights_used"] == 3
    assert sum(body["distribution"].values()) == 20
