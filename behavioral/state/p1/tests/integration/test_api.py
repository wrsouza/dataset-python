"""Integration tests for the Order State Machine API.

These tests use an in-memory SQLite database to avoid requiring PostgreSQL.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from orders.infrastructure.database import Base, get_db

SQLITE_URL = "sqlite:///./test_orders.db"

engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def override_get_db():  # type: ignore[return]
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db() -> None:  # type: ignore[return-value]
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield  # type: ignore[misc]
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def order_id(client: TestClient) -> str:
    resp = client.post(
        "/orders",
        json={
            "items": [
                {
                    "product_id": "p1",
                    "name": "Widget",
                    "quantity": 2,
                    "unit_price": 9.99,
                }
            ]
        },
    )
    assert resp.status_code == 201
    return resp.json()["order_id"]


def test_create_order(client: TestClient) -> None:
    resp = client.post(
        "/orders",
        json={
            "items": [
                {"product_id": "p1", "name": "Widget", "quantity": 1, "unit_price": 5.0}
            ]
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["state"] == "Pending"
    assert "pay" in data["allowed_transitions"]


def test_get_state(client: TestClient, order_id: str) -> None:
    resp = client.get(f"/orders/{order_id}/state")
    assert resp.status_code == 200
    assert resp.json()["state"] == "Pending"


def test_full_happy_path(client: TestClient, order_id: str) -> None:
    client.post(f"/orders/{order_id}/pay")
    client.post(f"/orders/{order_id}/ship")
    resp = client.post(f"/orders/{order_id}/deliver")
    assert resp.json()["state"] == "Delivered"


def test_history_grows(client: TestClient, order_id: str) -> None:
    client.post(f"/orders/{order_id}/pay")
    resp = client.get(f"/orders/{order_id}/history")
    assert len(resp.json()) == 1
    assert resp.json()[0]["to_state"] == "Paid"


def test_invalid_transition_returns_422(client: TestClient, order_id: str) -> None:
    resp = client.post(f"/orders/{order_id}/ship")
    assert resp.status_code == 422


def test_not_found_returns_404(client: TestClient) -> None:
    resp = client.get("/orders/nonexistent-id/state")
    assert resp.status_code == 404
