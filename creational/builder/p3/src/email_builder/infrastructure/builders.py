"""Concrete Email Builders for transactional emails."""

from __future__ import annotations

from typing import Self

from email_builder.domain.entities import Attachment, Email, TemplateType
from email_builder.domain.interfaces import EmailBuilder


class BaseEmailBuilder(EmailBuilder):
    """Shared state management — concrete builders inherit from here."""

    def __init__(self) -> None:
        self._subject: str = ""
        self._from_address: str = ""
        self._to_addresses: list[str] = []
        self._html_body: str = ""
        self._text_body: str = ""
        self._attachments: list[Attachment] = []
        self._template_type: TemplateType = TemplateType.WELCOME

    def set_subject(self, subject: str) -> Self:
        self._subject = subject
        return self

    def set_from(self, address: str) -> Self:
        self._from_address = address
        return self

    def set_to(self, *addresses: str) -> Self:
        self._to_addresses = list(addresses)
        return self

    def set_html_body(self, html: str) -> Self:
        self._html_body = html
        return self

    def set_text_body(self, text: str) -> Self:
        self._text_body = text
        return self

    def add_attachment(self, attachment: Attachment) -> Self:
        self._attachments.append(attachment)
        return self

    def build(self) -> Email:
        return Email(
            subject=self._subject,
            from_address=self._from_address,
            to_addresses=self._to_addresses,
            html_body=self._html_body,
            text_body=self._text_body,
            template_type=self._template_type,
            attachments=self._attachments,
        )


class WelcomeEmailBuilder(BaseEmailBuilder):
    """Builds welcome emails — sets sensible defaults for onboarding.

    SRP: only responsible for welcome email construction.
    """

    def __init__(self) -> None:
        super().__init__()
        self._template_type = TemplateType.WELCOME

    def with_user_name(self, name: str) -> Self:
        """Convenience method — sets subject and body with the user's name."""
        self._subject = f"Welcome to our platform, {name}!"
        self._html_body = (
            f"<h1>Welcome, {name}!</h1>"
            f"<p>We're thrilled to have you on board.</p>"
            f"<p>Get started by exploring your dashboard.</p>"
        )
        self._text_body = (
            f"Welcome, {name}!\n\n"
            "We're thrilled to have you on board.\n"
            "Get started by exploring your dashboard."
        )
        return self


class PasswordResetEmailBuilder(BaseEmailBuilder):
    """Builds password reset emails.

    SRP: only responsible for password-reset email construction.
    """

    def __init__(self) -> None:
        super().__init__()
        self._template_type = TemplateType.PASSWORD_RESET

    def with_reset_link(self, reset_url: str, expires_in_hours: int = 24) -> Self:
        """Sets subject and body with the password reset link."""
        self._subject = "Password Reset Request"
        self._html_body = (
            f"<h1>Reset Your Password</h1>"
            f"<p>Click the link below to reset your password. "
            f"It expires in {expires_in_hours} hours.</p>"
            f"<p><a href='{reset_url}'>Reset Password</a></p>"
            f"<p>If you did not request this, please ignore this email.</p>"
        )
        self._text_body = (
            "Reset Your Password\n\n"
            "Visit the following URL to reset your password "
            f"(expires in {expires_in_hours}h):\n"
            f"{reset_url}\n\n"
            "If you did not request this, please ignore this email."
        )
        return self


class OrderConfirmationEmailBuilder(BaseEmailBuilder):
    """Builds order confirmation emails.

    SRP: only responsible for order confirmation email construction.
    """

    def __init__(self) -> None:
        super().__init__()
        self._template_type = TemplateType.ORDER_CONFIRMATION

    def with_order_details(
        self,
        order_id: str,
        items: list[dict[str, str | float]],
        total: float,
    ) -> Self:
        """Sets subject and body with order details."""
        self._subject = f"Order Confirmation #{order_id}"
        items_html = "".join(
            f"<tr><td>{i['name']}</td><td>{i['qty']}</td><td>${i['price']:.2f}</td></tr>"
            for i in items
        )
        self._html_body = (
            f"<h1>Order Confirmed!</h1>"
            f"<p>Order #{order_id}</p>"
            f"<table><tr><th>Item</th><th>Qty</th><th>Price</th></tr>{items_html}</table>"
            f"<p><strong>Total: ${total:.2f}</strong></p>"
        )
        self._text_body = (
            f"Order Confirmed! Order #{order_id}\n\n"
            + "\n".join(f"- {i['name']} x{i['qty']} @ ${i['price']:.2f}" for i in items)
            + f"\n\nTotal: ${total:.2f}"
        )
        return self
