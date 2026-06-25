"""Application layer — use cases for sending notifications.

Use cases receive both the Notification (abstraction) and the payload.
They depend only on the Notification ABC, not on concrete types — DIP.
"""
from __future__ import annotations

from notifications.domain.entities import (
    Channel,
    DeliveryResult,
    NotificationPayload,
)
from notifications.domain.interfaces import Notification, NotificationSender
from notifications.domain.notifications import (
    AlertNotification,
    ReportNotification,
    WelcomeNotification,
)
from notifications.infrastructure.implementations import (
    EmailSender,
    PushSender,
    SMSSender,
)


class SendNotificationUseCase:
    """Orchestrates building the right Notification × Sender combination.

    This is the composition root for the Bridge pattern:
    it selects the abstraction (type) and the implementation (channel)
    independently and wires them together.
    """

    _SENDER_FACTORY: dict[Channel, type[NotificationSender]] = {
        Channel.EMAIL: EmailSender,
        Channel.SMS: SMSSender,
        Channel.PUSH: PushSender,
    }

    def __init__(
        self,
        email_sender_address: str = "noreply@example.com",
        ses_endpoint_url: str | None = None,
    ) -> None:
        self._email_address = email_sender_address
        self._ses_endpoint = ses_endpoint_url

    def _build_sender(self, channel: Channel) -> NotificationSender:
        if channel == Channel.EMAIL:
            return EmailSender(
                sender_address=self._email_address,
                endpoint_url=self._ses_endpoint,
            )
        if channel == Channel.SMS:
            return SMSSender()
        return PushSender()

    def send_alert(
        self,
        recipient: str,
        channel: Channel,
        payload: NotificationPayload,
    ) -> DeliveryResult:
        sender = self._build_sender(channel)
        notification: Notification = AlertNotification(sender=sender)
        return notification.send(recipient, payload)

    def send_report(
        self,
        recipient: str,
        channel: Channel,
        payload: NotificationPayload,
    ) -> DeliveryResult:
        sender = self._build_sender(channel)
        notification: Notification = ReportNotification(sender=sender)
        return notification.send(recipient, payload)

    def send_welcome(
        self,
        recipient: str,
        channel: Channel,
        payload: NotificationPayload,
    ) -> DeliveryResult:
        sender = self._build_sender(channel)
        notification: Notification = WelcomeNotification(sender=sender)
        return notification.send(recipient, payload)
