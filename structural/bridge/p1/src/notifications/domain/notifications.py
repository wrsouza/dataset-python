"""Refined Abstractions — concrete notification types.

Each class knows how to format its own content; it delegates delivery
to the injected NotificationSender (bridge).
"""
from __future__ import annotations

from notifications.domain.entities import (
    DeliveryResult,
    NotificationPayload,
)
from notifications.domain.interfaces import Notification


class AlertNotification(Notification):
    """Sends operational alerts with severity and source context."""

    def send(self, recipient: str, data: NotificationPayload) -> DeliveryResult:
        severity = data.get("severity", "INFO")
        message = data.get("message", "No message provided")
        source = data.get("source", "system")

        subject = f"[{severity.upper()}] Alert from {source}"
        body = (
            f"Alert Notification\n"
            f"==================\n"
            f"Severity : {severity.upper()}\n"
            f"Source   : {source}\n"
            f"Message  : {message}\n"
        )
        return self._sender.deliver(to=recipient, subject=subject, body=body)


class ReportNotification(Notification):
    """Sends periodic report summaries with a download link."""

    def send(self, recipient: str, data: NotificationPayload) -> DeliveryResult:
        report_name = data.get("report_name", "Report")
        period = data.get("period", "N/A")
        summary = data.get("summary", "")
        download_url = data.get("download_url", "")

        subject = f"Report Ready: {report_name} ({period})"
        body = (
            f"Report Notification\n"
            f"===================\n"
            f"Report  : {report_name}\n"
            f"Period  : {period}\n"
            f"Summary : {summary}\n"
            f"Download: {download_url}\n"
        )
        return self._sender.deliver(to=recipient, subject=subject, body=body)


class WelcomeNotification(Notification):
    """Sends onboarding welcome messages with an activation link."""

    def send(self, recipient: str, data: NotificationPayload) -> DeliveryResult:
        user_name = data.get("user_name", "User")
        activation_link = data.get("activation_link", "")

        subject = f"Welcome to the platform, {user_name}!"
        body = (
            f"Welcome!\n"
            f"========\n"
            f"Hi {user_name},\n\n"
            f"Your account has been created successfully.\n"
            f"Activate your account here: {activation_link}\n"
        )
        return self._sender.deliver(to=recipient, subject=subject, body=body)
