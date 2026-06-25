"""Integration tests for the realtime_notifications Django views."""

from __future__ import annotations

import json

import pytest
from django.test import AsyncClient

pytestmark = pytest.mark.django_db


@pytest.mark.asyncio
async def test_publish_notification_persists_and_returns_201() -> None:
    client = AsyncClient()

    response = await client.post(
        "/notifications/room-1/",
        data=json.dumps({"message": {"text": "hello"}}),
        content_type="application/json",
    )

    assert response.status_code == 201
    assert response.json()["group"] == "room-1"


@pytest.mark.asyncio
async def test_list_notifications_returns_published_notifications() -> None:
    client = AsyncClient()
    await client.post(
        "/notifications/room-1/",
        data=json.dumps({"message": {"text": "hello"}}),
        content_type="application/json",
    )

    response = await client.get("/notifications/room-1/list/")

    body = response.json()
    assert len(body) >= 1
    assert all(n["message"] == {"text": "hello"} for n in body)
