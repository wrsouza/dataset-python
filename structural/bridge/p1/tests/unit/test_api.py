"""Unit tests for FastAPI routes using dependency override."""
from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient

from notifications.domain.entities import Channel, DeliveryResult, DeliveryStatus


@pytest.fixture()
def client() -> TestClient:
    """Return a test client with SMS/Push senders (no real AWS calls)."""
    from main import app
    return TestClient(app)


class TestAlertRoute:
    def test_post_alert_sms_returns_201(self, client: TestClient) -> None:
        response = client.post(
            "/notifications/alert",
            json={
                "recipient": "+5511999990000",
                "channel": "sms",
                "severity": "CRITICAL",
                "message": "Database unreachable",
                "source": "monitor",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "sent"
        assert data["channel"] == "sms"

    def test_post_alert_push_returns_201(self, client: TestClient) -> None:
        response = client.post(
            "/notifications/alert",
            json={
                "recipient": "device-token-xyz",
                "channel": "push",
                "severity": "WARNING",
                "message": "High memory",
                "source": "agent",
            },
        )
        assert response.status_code == 201

    def test_post_alert_invalid_channel_returns_422(self, client: TestClient) -> None:
        response = client.post(
            "/notifications/alert",
            json={
                "recipient": "ops@example.com",
                "channel": "telegram",
                "message": "test",
            },
        )
        assert response.status_code == 422


class TestReportRoute:
    def test_post_report_sms_returns_201(self, client: TestClient) -> None:
        response = client.post(
            "/notifications/report",
            json={
                "recipient": "+1234567890",
                "channel": "sms",
                "report_name": "Sales Q1",
                "period": "2024-Q1",
                "summary": "Up 12%",
                "download_url": "https://example.com/report.pdf",
            },
        )
        assert response.status_code == 201
        assert response.json()["status"] == "sent"


class TestWelcomeRoute:
    def test_post_welcome_push_returns_201(self, client: TestClient) -> None:
        response = client.post(
            "/notifications/welcome",
            json={
                "recipient": "device-abc",
                "channel": "push",
                "user_name": "Alice",
                "activation_link": "https://app.example.com/activate/abc",
            },
        )
        assert response.status_code == 201


class TestHealthRoute:
    def test_health_returns_ok(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
