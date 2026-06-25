"""Integration tests for Document Version History API.

Requires DATABASE_URL pointing to a running PostgreSQL instance.
Run with: docker compose up -d db && pytest tests/integration
"""
from __future__ import annotations

import os

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

pytestmark = pytest.mark.skipif(
    os.getenv("DATABASE_URL") is None,
    reason="DATABASE_URL not set — skipping integration tests",
)


@pytest_asyncio.fixture
async def client():  # type: ignore[no-untyped-def]
    from main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_create_and_get_history(client: AsyncClient) -> None:
    resp = await client.post(
        "/documents",
        json={"title": "My Doc", "content": "Hello", "metadata": {}, "author": "alice"},
    )
    assert resp.status_code == 201
    doc_id = resp.json()["id"]

    resp = await client.get(f"/documents/{doc_id}/history")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["version"] == 1


@pytest.mark.asyncio
async def test_edit_creates_new_version(client: AsyncClient) -> None:
    resp = await client.post(
        "/documents",
        json={"title": "Doc", "content": "v1", "metadata": {}, "author": "alice"},
    )
    doc_id = resp.json()["id"]

    await client.put(
        f"/documents/{doc_id}",
        json={"content": "v2", "metadata": {}, "author": "bob"},
    )

    resp = await client.get(f"/documents/{doc_id}/history")
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_restore_version(client: AsyncClient) -> None:
    resp = await client.post(
        "/documents",
        json={"title": "Doc", "content": "original", "metadata": {}, "author": "alice"},
    )
    doc_id = resp.json()["id"]

    await client.put(
        f"/documents/{doc_id}",
        json={"content": "changed", "metadata": {}, "author": "bob"},
    )

    resp = await client.post(f"/documents/{doc_id}/restore/1")
    assert resp.status_code == 200
    # After restore, content should match version 1
    assert resp.json()["content"] == "original"


@pytest.mark.asyncio
async def test_undo_returns_previous_state(client: AsyncClient) -> None:
    resp = await client.post(
        "/documents",
        json={"title": "Doc", "content": "first", "metadata": {}, "author": "alice"},
    )
    doc_id = resp.json()["id"]

    await client.put(
        f"/documents/{doc_id}",
        json={"content": "second", "metadata": {}, "author": "bob"},
    )

    resp = await client.post(f"/documents/{doc_id}/undo")
    assert resp.status_code == 200
    assert resp.json()["content"] == "first"
