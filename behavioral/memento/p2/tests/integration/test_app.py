"""Integration tests for the Flask Form State Save/Restore API."""

from __future__ import annotations

from flask.testing import FlaskClient


def test_health_check(client: FlaskClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_save_form_state(client: FlaskClient) -> None:
    response = client.post(
        "/forms/session-1",
        json={"fields": {"name": "Ana"}, "step": 1, "label": "manual"},
    )

    body = response.get_json()
    assert response.status_code == 201
    assert body["fields"] == {"name": "Ana"}
    assert body["step"] == 1
    assert body["label"] == "manual"


def test_save_form_state_merges_across_calls(client: FlaskClient) -> None:
    client.post("/forms/session-1", json={"fields": {"name": "Ana"}, "step": 1})
    response = client.post(
        "/forms/session-1", json={"fields": {"email": "a@b.com"}, "step": 2}
    )

    body = response.get_json()
    assert body["fields"] == {"name": "Ana", "email": "a@b.com"}


def test_get_form_state_after_save(client: FlaskClient) -> None:
    client.post("/forms/session-1", json={"fields": {"name": "Ana"}, "step": 1})

    response = client.get("/forms/session-1")

    assert response.status_code == 200
    assert response.get_json()["fields"] == {"name": "Ana"}


def test_get_form_state_unknown_session_returns_404(client: FlaskClient) -> None:
    response = client.get("/forms/does-not-exist")

    assert response.status_code == 404


def test_undo_form_state(client: FlaskClient) -> None:
    client.post("/forms/session-1", json={"fields": {"a": 1}, "step": 1})
    client.post("/forms/session-1", json={"fields": {"b": 2}, "step": 2})

    response = client.post("/forms/session-1/undo")

    body = response.get_json()
    assert response.status_code == 200
    assert body["step"] == 1
    assert body["fields"] == {"a": 1}


def test_undo_form_state_without_history_returns_404(client: FlaskClient) -> None:
    response = client.post("/forms/does-not-exist/undo")

    assert response.status_code == 404


def test_get_form_history(client: FlaskClient) -> None:
    client.post("/forms/session-1", json={"fields": {"a": 1}, "step": 1})
    client.post("/forms/session-1", json={"fields": {"b": 2}, "step": 2})

    response = client.get("/forms/session-1/history")

    body = response.get_json()
    assert response.status_code == 200
    assert [item["step"] for item in body] == [1, 2]
