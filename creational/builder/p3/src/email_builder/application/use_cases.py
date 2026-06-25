"""Director and use cases for the Email Builder."""

from __future__ import annotations

from email_builder.domain.entities import Email, SendResult
from email_builder.domain.interfaces import EmailBuilder, EmailSender
from email_builder.infrastructure.builders import (
    OrderConfirmationEmailBuilder,
    PasswordResetEmailBuilder,
    WelcomeEmailBuilder,
)


class CampaignDirector:
    """Director that orchestrates the email construction sequence.

    DIP: depends on EmailBuilder abstraction and EmailSender protocol.
    """

    DEFAULT_FROM = "noreply@example.com"

    def build_welcome(self, recipient: str, user_name: str) -> Email:
        return (
            WelcomeEmailBuilder()
            .set_from(self.DEFAULT_FROM)
            .set_to(recipient)
            .with_user_name(user_name)
            .build()
        )

    def build_password_reset(self, recipient: str, reset_url: str) -> Email:
        return (
            PasswordResetEmailBuilder()
            .set_from(self.DEFAULT_FROM)
            .set_to(recipient)
            .with_reset_link(reset_url)
            .build()
        )

    def build_order_confirmation(
        self,
        recipient: str,
        order_id: str,
        items: list[dict[str, str | float]],
        total: float,
    ) -> Email:
        return (
            OrderConfirmationEmailBuilder()
            .set_from(self.DEFAULT_FROM)
            .set_to(recipient)
            .with_order_details(order_id, items, total)
            .build()
        )


class SendEmailUseCase:
    """Builds an email via a provided builder and sends it via the sender port."""

    def __init__(self, builder: EmailBuilder, sender: EmailSender) -> None:
        self._builder = builder
        self._sender = sender

    def execute(self, email: Email) -> SendResult:
        return self._sender.send(email)


class SendCampaignEmailUseCase:
    """Convenience use case: build + send using the Director."""

    def __init__(self, sender: EmailSender) -> None:
        self._director = CampaignDirector()
        self._sender = sender

    def send_welcome(self, recipient: str, user_name: str) -> SendResult:
        email = self._director.build_welcome(recipient, user_name)
        return self._sender.send(email)

    def send_password_reset(self, recipient: str, reset_url: str) -> SendResult:
        email = self._director.build_password_reset(recipient, reset_url)
        return self._sender.send(email)

    def send_order_confirmation(
        self,
        recipient: str,
        order_id: str,
        items: list[dict[str, str | float]],
        total: float,
    ) -> SendResult:
        email = self._director.build_order_confirmation(
            recipient, order_id, items, total
        )
        return self._sender.send(email)
