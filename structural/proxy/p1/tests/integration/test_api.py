"""Integration tests for the FastAPI app — real HTTP routing, fake RealSubject.

main.py's lifespan creates a real asyncpg pool on startup; for tests we
monkeypatch asyncpg.create_pool so startup never touches a real network
connection, then override the get_proxy dependency to serve a Proxy backed
by FakeUserProfileService — the full HTTP -> use case -> Proxy flow runs for
real, only the bottom-most asyncpg/Postgres layer is replaced.
"""

from __future__ import annotations

from collections.abc import Iterator
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

import main as main_module
from lazy_loading.infrastructure.proxy import LazyUserProfileProxy
from tests.conftest import FakeUserProfileService


class _FakePool:
    async def close(self) -> None:
        return None


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setattr(
        main_module.asyncpg, "create_pool", AsyncMock(return_value=_FakePool())
    )

    fake_service = FakeUserProfileService()
    fake_proxy = LazyUserProfileProxy(real_service=fake_service)

    with TestClient(main_module.app) as test_client:
        main_module.app.dependency_overrides[main_module.get_proxy] = lambda: fake_proxy
        yield test_client
    main_module.app.dependency_overrides.clear()


def test_get_profile_returns_200(client: TestClient) -> None:
    response = client.get("/users/1/profile")

    assert response.status_code == 200
    assert response.json()["username"] == "alice"


def test_get_profile_returns_404_for_unknown_user(client: TestClient) -> None:
    response = client.get("/users/999/profile")

    assert response.status_code == 404


def test_get_avatar_returns_404_when_missing(client: TestClient) -> None:
    response = client.get("/users/2/avatar")

    assert response.status_code == 404


def test_get_documents_returns_list(client: TestClient) -> None:
    response = client.get("/users/1/documents")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_analytics_returns_200(client: TestClient) -> None:
    response = client.get("/users/1/analytics")

    assert response.status_code == 200
    assert response.json()["login_count"] == 2


def test_load_stats_reflect_cache_behaviour(client: TestClient) -> None:
    client.get("/users/1/profile")
    client.get("/users/1/profile")

    response = client.get("/profile/load-stats")

    assert response.status_code == 200
    body = response.json()
    assert body["profile_loads"] == 1
    assert body["profile_cache_hits"] == 1
