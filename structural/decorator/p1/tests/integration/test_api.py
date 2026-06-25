"""Integration tests for the FastAPI endpoints.

Tests the full HTTP layer using httpx's async test client.
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.fixture
async def client() -> AsyncClient:  # type: ignore[misc]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_protected_endpoint_with_valid_auth(client: AsyncClient) -> None:
    response = await client.get(
        "/api/protected/resource",
        headers={"Authorization": "Bearer valid-jwt-token"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_protected_endpoint_without_auth_returns_401(client: AsyncClient) -> None:
    response = await client.get("/api/protected/resource")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_public_endpoint_without_auth(client: AsyncClient) -> None:
    response = await client.get("/api/public/resource")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_minimal_endpoint(client: AsyncClient) -> None:
    response = await client.get("/api/minimal")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient) -> None:
    response = await client.get("/")
    data = response.json()
    assert data["pattern"] == "Decorator (GoF)"
