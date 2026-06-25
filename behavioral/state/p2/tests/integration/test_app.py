"""Integration tests for the Flask User Auth Session FSM API."""

from __future__ import annotations

from flask.testing import FlaskClient


def test_health_check(client: FlaskClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_successful_login_activates_session(client: FlaskClient) -> None:
    response = client.post("/sessions/s1/login", json={"success": True})

    body = response.get_json()
    assert response.status_code == 200
    assert body["state"] == "Active"


def test_failed_logins_lock_session_after_three_attempts(client: FlaskClient) -> None:
    for _ in range(3):
        response = client.post("/sessions/s1/login", json={"success": False})

    assert response.get_json()["state"] == "Locked"


def test_get_session_returns_404_for_unknown_session(client: FlaskClient) -> None:
    response = client.get("/sessions/unknown")

    assert response.status_code == 404


def test_get_session_after_login(client: FlaskClient) -> None:
    client.post("/sessions/s1/login", json={"success": True})

    response = client.get("/sessions/s1")

    assert response.status_code == 200
    assert response.get_json()["state"] == "Active"


def test_logout_returns_session_to_anonymous(client: FlaskClient) -> None:
    client.post("/sessions/s1/login", json={"success": True})

    response = client.post("/sessions/s1/logout")

    assert response.status_code == 200
    assert response.get_json()["state"] == "Anonymous"


def test_invalid_transition_returns_409(client: FlaskClient) -> None:
    response = client.post("/sessions/s1/unlock")

    assert response.status_code == 409


def test_expire_then_relogin(client: FlaskClient) -> None:
    client.post("/sessions/s1/login", json={"success": True})
    client.post("/sessions/s1/expire")

    response = client.post("/sessions/s1/login", json={"success": True})

    assert response.get_json()["state"] == "Active"


def test_refresh_on_anonymous_session_returns_409(client: FlaskClient) -> None:
    response = client.post("/sessions/s1/refresh")

    assert response.status_code == 409


def test_expire_on_anonymous_session_returns_409(client: FlaskClient) -> None:
    response = client.post("/sessions/s1/expire")

    assert response.status_code == 409


def test_unlock_resets_locked_session(client: FlaskClient) -> None:
    for _ in range(3):
        client.post("/sessions/s1/login", json={"success": False})

    response = client.post("/sessions/s1/unlock")

    assert response.status_code == 200
    assert response.get_json()["state"] == "Anonymous"
