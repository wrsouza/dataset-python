"""Integration tests for the Flask ticket escalation API."""

from __future__ import annotations

from flask.testing import FlaskClient


def test_health_check(client: FlaskClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_submit_low_severity_ticket_resolves_at_tier_1(client: FlaskClient) -> None:
    response = client.post(
        "/tickets",
        json={
            "subject": "Forgot password",
            "severity": "low",
            "customer_email": "user@example.com",
        },
    )

    body = response.get_json()
    assert response.status_code == 201
    assert body["is_resolved"] is True
    assert body["resolved_by"] == "tier_1"


def test_submit_critical_ticket_escalates_to_management(client: FlaskClient) -> None:
    response = client.post(
        "/tickets",
        json={
            "subject": "Full outage",
            "severity": "critical",
            "customer_email": "vip@example.com",
        },
    )

    body = response.get_json()
    assert body["resolved_by"] == "management"


def test_get_ticket_after_submission(client: FlaskClient) -> None:
    submit_response = client.post(
        "/tickets",
        json={
            "subject": "Login issue",
            "severity": "medium",
            "customer_email": "user2@example.com",
        },
    )
    ticket_id = submit_response.get_json()["ticket_id"]

    get_response = client.get(f"/tickets/{ticket_id}")

    assert get_response.status_code == 200
    assert get_response.get_json()["ticket_id"] == ticket_id


def test_get_unknown_ticket_returns_404(client: FlaskClient) -> None:
    response = client.get("/tickets/does-not-exist")

    assert response.status_code == 404
