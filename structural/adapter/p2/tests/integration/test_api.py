"""Integration tests — Flask routes with in-memory SQLite via SQLAlchemy adapter."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from orm_adapter.infrastructure.sqlalchemy_adapter import SQLAlchemyUserAdapter, _Base


@pytest.fixture(autouse=True)
def sqlite_adapter():
    """Override _get_repository in main to use an in-memory SQLite adapter."""
    engine = create_engine("sqlite:///:memory:")
    _Base.metadata.create_all(engine)
    session = Session(engine)
    adapter = SQLAlchemyUserAdapter(session=session)

    with patch("orm_adapter.main._get_repository", return_value=adapter):
        yield adapter


@pytest.fixture
def client():
    from orm_adapter.main import app

    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestUserCRUD:
    def test_create_user(self, client) -> None:
        resp = client.post("/users", json={"name": "Alice", "email": "alice@test.com"})
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["name"] == "Alice"
        assert data["id"] > 0

    def test_list_users(self, client) -> None:
        client.post("/users", json={"name": "Bob", "email": "bob@test.com"})
        resp = client.get("/users")
        assert resp.status_code == 200
        assert len(resp.get_json()) >= 1

    def test_get_user(self, client) -> None:
        created = client.post(
            "/users", json={"name": "Carol", "email": "carol@test.com"}
        ).get_json()
        resp = client.get(f"/users/{created['id']}")
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "Carol"

    def test_get_user_not_found(self, client) -> None:
        resp = client.get("/users/9999")
        assert resp.status_code == 404

    def test_delete_user(self, client) -> None:
        created = client.post(
            "/users", json={"name": "Dave", "email": "dave@test.com"}
        ).get_json()
        resp = client.delete(f"/users/{created['id']}")
        assert resp.status_code == 200

    def test_health(self, client) -> None:
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_update_user(self, client) -> None:
        created = client.post(
            "/users", json={"name": "Eve", "email": "eve@test.com"}
        ).get_json()
        resp = client.put(
            f"/users/{created['id']}",
            json={"name": "Eve Updated", "email": "eve2@test.com"},
        )
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "Eve Updated"

    def test_update_user_not_found(self, client) -> None:
        resp = client.put(
            "/users/9999", json={"name": "Nobody", "email": "nobody@test.com"}
        )
        assert resp.status_code == 404

    def test_delete_user_not_found(self, client) -> None:
        resp = client.delete("/users/9999")
        assert resp.status_code == 404
