"""Unit tests for the Bridge pattern — Notification domain.

Uses fakes (in-memory senders) to test each notification type
independently of real delivery channels.
"""
from __future__ import annotations

import pytest

from notifications.domain.entities import (
    Channel,
    DeliveryResult,
    DeliveryStatus,
    NotificationPayload,
)
from notifications.domain.interfaces import NotificationSender
from notifications.domain.notifications import (
    AlertNotification,
    ReportNotification,
    WelcomeNotification,
)


class FakeSender(NotificationSender):
    """In-memory sender that records calls for assertion."""

    def __init__(self, channel: Channel = Channel.EMAIL) -> None:
        self.calls: list[dict[str, str]] = []
        self._channel = channel

    def deliver(self, to: str, subject: str, body: str) -> DeliveryResult:
        self.calls.append({"to": to, "subject": subject, "body": body})
        return DeliveryResult(
            status=DeliveryStatus.SENT,
            message_id="fake-001",
            channel=self._channel,
        )


class FailingSender(NotificationSender):
    """Always returns a FAILED result to test error paths."""

    def deliver(self, to: str, subject: str, body: str) -> DeliveryResult:
        return DeliveryResult(
            status=DeliveryStatus.FAILED,
            message_id="",
            channel=Channel.EMAIL,
            error="Connection refused",
        )


# ── AlertNotification tests ────────────────────────────────────────────────────

class TestAlertNotification:
    def test_send_returns_success(self) -> None:
        sender = FakeSender()
        notification = AlertNotification(sender=sender)
        payload = NotificationPayload(
            data={"severity": "CRITICAL", "message": "Disk full", "source": "monitor"}
        )

        result = notification.send("ops@example.com", payload)

        assert result.is_successful
        assert result.message_id == "fake-001"

    def test_subject_contains_severity(self) -> None:
        sender = FakeSender()
        notification = AlertNotification(sender=sender)
        payload = NotificationPayload(
            data={"severity": "warning", "message": "High CPU", "source": "agent"}
        )

        notification.send("ops@example.com", payload)

        assert "WARNING" in sender.calls[0]["subject"]

    def test_body_contains_all_fields(self) -> None:
        sender = FakeSender()
        notification = AlertNotification(sender=sender)
        payload = NotificationPayload(
            data={"severity": "INFO", "message": "Service restarted", "source": "k8s"}
        )

        notification.send("ops@example.com", payload)
        body = sender.calls[0]["body"]

        assert "Service restarted" in body
        assert "k8s" in body

    def test_defaults_when_payload_empty(self) -> None:
        sender = FakeSender()
        notification = AlertNotification(sender=sender)
        payload = NotificationPayload()

        result = notification.send("ops@example.com", payload)

        assert result.is_successful
        assert sender.calls[0]["subject"] != ""

    def test_failing_sender_returns_failed_result(self) -> None:
        notification = AlertNotification(sender=FailingSender())
        payload = NotificationPayload(data={"message": "test"})

        result = notification.send("ops@example.com", payload)

        assert result.status == DeliveryStatus.FAILED
        assert not result.is_successful


# ── ReportNotification tests ───────────────────────────────────────────────────

class TestReportNotification:
    def test_send_returns_success(self) -> None:
        sender = FakeSender()
        notification = ReportNotification(sender=sender)
        payload = NotificationPayload(
            data={
                "report_name": "Sales Q1",
                "period": "2024-Q1",
                "summary": "Revenue up 12%",
                "download_url": "https://example.com/report.pdf",
            }
        )

        result = notification.send("manager@example.com", payload)

        assert result.is_successful

    def test_subject_contains_report_name(self) -> None:
        sender = FakeSender()
        notification = ReportNotification(sender=sender)
        payload = NotificationPayload(
            data={
                "report_name": "Inventory Summary",
                "period": "2024-W20",
                "summary": "",
                "download_url": "",
            }
        )

        notification.send("manager@example.com", payload)

        assert "Inventory Summary" in sender.calls[0]["subject"]

    def test_body_contains_download_url(self) -> None:
        sender = FakeSender()
        notification = ReportNotification(sender=sender)
        url = "https://storage.example.com/rep.xlsx"
        payload = NotificationPayload(
            data={
                "report_name": "R",
                "period": "P",
                "summary": "S",
                "download_url": url,
            }
        )

        notification.send("user@example.com", payload)

        assert url in sender.calls[0]["body"]


# ── WelcomeNotification tests ──────────────────────────────────────────────────

class TestWelcomeNotification:
    def test_send_returns_success(self) -> None:
        sender = FakeSender()
        notification = WelcomeNotification(sender=sender)
        payload = NotificationPayload(
            data={
                "user_name": "Alice",
                "activation_link": "https://app.example.com/activate/abc123",
            }
        )

        result = notification.send("alice@example.com", payload)

        assert result.is_successful

    def test_subject_contains_user_name(self) -> None:
        sender = FakeSender()
        notification = WelcomeNotification(sender=sender)
        payload = NotificationPayload(
            data={"user_name": "Bob", "activation_link": "https://example.com"}
        )

        notification.send("bob@example.com", payload)

        assert "Bob" in sender.calls[0]["subject"]

    def test_body_contains_activation_link(self) -> None:
        sender = FakeSender()
        notification = WelcomeNotification(sender=sender)
        link = "https://app.example.com/activate/xyz789"
        payload = NotificationPayload(
            data={"user_name": "Carol", "activation_link": link}
        )

        notification.send("carol@example.com", payload)

        assert link in sender.calls[0]["body"]


# ── Bridge combination tests ───────────────────────────────────────────────────

class TestBridgeCombinations:
    """Verify that any notification type works with any sender channel."""

    @pytest.mark.parametrize(
        "notification_cls",
        [AlertNotification, ReportNotification, WelcomeNotification],
    )
    @pytest.mark.parametrize(
        "channel",
        [Channel.EMAIL, Channel.SMS, Channel.PUSH],
    )
    def test_all_combinations_succeed(
        self,
        notification_cls: type,
        channel: Channel,
    ) -> None:
        sender = FakeSender(channel=channel)
        notification = notification_cls(sender=sender)
        payload = NotificationPayload(
            data={
                "severity": "INFO",
                "message": "test",
                "source": "test",
                "report_name": "R",
                "period": "P",
                "summary": "S",
                "download_url": "",
                "user_name": "User",
                "activation_link": "http://example.com",
            }
        )

        result = notification.send("recipient@example.com", payload)

        assert result.is_successful
        assert result.channel == channel
