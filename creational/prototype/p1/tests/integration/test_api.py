"""Integration tests for the FastAPI endpoints."""
from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.mark.asyncio
async def test_list_templates() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/characters/templates")
    assert response.status_code == 200
    data = response.json()
    assert "warrior" in data["templates"]
    assert "mage" in data["templates"]


@pytest.mark.asyncio
async def test_clone_unknown_template_returns_404() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/characters/clone/paladin", json={"overrides": {}}
        )
    assert response.status_code == 404
