"""Integration tests for the Django Email Builder API — SES mocked via moto."""

from __future__ import annotations

import json

import boto3
import pytest
from django.test import Client
from moto import mock_aws

from email_builder.models import EmailLog

VERIFIED_SENDER = "noreply@example.com"

pytestmark = pytest.mark.django_db


@pytest.fixture
def mocked_ses(monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    monkeypatch.delenv("AWS_ENDPOINT_URL", raising=False)
    with mock_aws():
        client = boto3.client(
            "ses",
            region_name="us-east-1",
            aws_access_key_id="test",  # noqa: S106
            aws_secret_access_key="test",  # noqa: S106
        )
        client.verify_email_identity(EmailAddress=VERIFIED_SENDER)
        yield client


class TestHealthCheck:
    def test_health_returns_ok(self, api_client: Client) -> None:
        response = api_client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestSendEmailView:
    def test_send_welcome_email_creates_log_and_returns_success(
        self, api_client: Client, mocked_ses
    ) -> None:
        response = api_client.post(
            "/emails/welcome",
            data=json.dumps({"recipient": "alice@example.com", "user_name": "Alice"}),
            content_type="application/json",
        )

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "sent"
        assert EmailLog.objects.count() == 1
        log = EmailLog.objects.first()
        assert log is not None
        assert log.recipient == "alice@example.com"
        assert log.status == "sent"

    def test_send_password_reset_email(self, api_client: Client, mocked_ses) -> None:
        response = api_client.post(
            "/emails/password_reset",
            data=json.dumps(
                {"recipient": "bob@example.com", "reset_url": "https://x.test/reset"}
            ),
            content_type="application/json",
        )

        assert response.status_code == 200
        assert response.json()["status"] == "sent"

    def test_send_order_confirmation_email(
        self, api_client: Client, mocked_ses
    ) -> None:
        response = api_client.post(
            "/emails/order_confirmation",
            data=json.dumps(
                {
                    "recipient": "carol@example.com",
                    "order_id": "ORD-9",
                    "items": [{"name": "Widget", "qty": 1, "price": 9.99}],
                    "total": 9.99,
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 200
        assert response.json()["status"] == "sent"

    def test_missing_recipient_returns_400(
        self, api_client: Client, mocked_ses
    ) -> None:
        response = api_client.post(
            "/emails/welcome",
            data=json.dumps({"user_name": "Alice"}),
            content_type="application/json",
        )

        assert response.status_code == 400

    def test_unknown_template_type_returns_404(
        self, api_client: Client, mocked_ses
    ) -> None:
        response = api_client.post(
            "/emails/unknown_type",
            data=json.dumps({"recipient": "alice@example.com"}),
            content_type="application/json",
        )

        assert response.status_code == 404

    def test_invalid_json_returns_400(self, api_client: Client, mocked_ses) -> None:
        response = api_client.post(
            "/emails/welcome",
            data="not-json",
            content_type="application/json",
        )

        assert response.status_code == 400

    def test_unverified_sender_logs_failure(
        self, api_client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("AWS_ENDPOINT_URL", raising=False)
        with mock_aws():
            response = api_client.post(
                "/emails/welcome",
                data=json.dumps(
                    {"recipient": "alice@example.com", "user_name": "Alice"}
                ),
                content_type="application/json",
            )

            assert response.status_code == 500
            log = EmailLog.objects.first()
            assert log is not None
            assert log.status == "failed"


class TestEmailLogListView:
    def test_list_logs_returns_created_logs(
        self, api_client: Client, mocked_ses
    ) -> None:
        api_client.post(
            "/emails/welcome",
            data=json.dumps({"recipient": "alice@example.com", "user_name": "Alice"}),
            content_type="application/json",
        )

        response = api_client.get("/emails/logs")

        assert response.status_code == 200
        body = response.json()
        assert body["count"] == 1
        assert body["logs"][0]["recipient"] == "alice@example.com"

    def test_list_logs_empty(self, api_client: Client) -> None:
        response = api_client.get("/emails/logs")
        assert response.status_code == 200
        assert response.json()["count"] == 0
