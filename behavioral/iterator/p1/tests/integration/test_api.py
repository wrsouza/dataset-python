"""Integration tests for the FastAPI order pagination/export endpoints."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from order_pagination.main import app, get_repository
from tests.unit.test_cursor_iterator import FakeOrderRepository


@pytest.fixture
def client() -> Iterator[TestClient]:
    app.dependency_overrides[get_repository] = lambda: FakeOrderRepository(total=10)
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_orders_returns_first_page(client: TestClient) -> None:
    response = client.get("/orders", params={"limit": 4})

    body = response.json()
    assert [item["order_id"] for item in body["items"]] == [1, 2, 3, 4]
    assert body["next_cursor"] == "4"


def test_list_orders_follows_cursor_to_next_page(client: TestClient) -> None:
    first = client.get("/orders", params={"limit": 4}).json()

    second = client.get(
        "/orders", params={"limit": 4, "cursor": first["next_cursor"]}
    ).json()

    assert [item["order_id"] for item in second["items"]] == [5, 6, 7, 8]


def test_export_orders_streams_every_order(client: TestClient) -> None:
    response = client.get("/orders/export")

    lines = [line for line in response.text.splitlines() if line]
    assert len(lines) == 10
