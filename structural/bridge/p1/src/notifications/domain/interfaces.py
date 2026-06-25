"""Bridge pattern interfaces — Notification domain.

Two independent hierarchies:
- Abstraction: Notification (what to send)
- Implementation: NotificationSender (how/where to deliver)
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from notifications.domain.entities import DeliveryResult, NotificationPayload


class NotificationSender(ABC):
    """Implementation hierarchy — delivery channel.

    Concrete implementations decide HOW to deliver a message
    (email, SMS, push). They know nothing about notification types.
    """

    @abstractmethod
    def deliver(
        self,
        to: str,
        subject: str,
        body: str,
    ) -> DeliveryResult:
        """Deliver a message to a recipient.

        Args:
            to: Recipient address (email, phone, device token).
            subject: Short summary line.
            body: Full message body.

        Returns:
            DeliveryResult with status and provider message ID.
        """


class Notification(ABC):
    """Abstraction hierarchy — notification type.

    Subclasses know WHAT content to build; they delegate delivery
    to the injected ``sender`` (the bridge).
    """

    def __init__(self, sender: NotificationSender) -> None:
        # Bridge: composition over inheritance for the delivery channel.
        self._sender = sender

    @abstractmethod
    def send(self, recipient: str, data: NotificationPayload) -> DeliveryResult:
        """Build type-specific content and forward to sender.

        Args:
            recipient: Destination address appropriate for the channel.
            data: Flexible payload parsed by each notification subtype.
        """
