"""Unit tests for the Email Builder pattern — no Django DB, no network."""

from __future__ import annotations

import pytest

from email_builder.application.use_cases import (
    CampaignDirector,
    SendCampaignEmailUseCase,
    SendEmailUseCase,
)
from email_builder.domain.entities import Attachment, Email, SendResult, TemplateType
from email_builder.infrastructure.builders import (
    OrderConfirmationEmailBuilder,
    PasswordResetEmailBuilder,
    WelcomeEmailBuilder,
)

pytestmark = pytest.mark.django_db


class FakeEmailSender:
    """Test double for the EmailSender protocol — no boto3, no network."""

    def __init__(self, succeed: bool = True) -> None:
        self.succeed = succeed
        self.sent_emails: list[Email] = []

    def send(self, email: Email) -> SendResult:
        self.sent_emails.append(email)
        if self.succeed:
            return SendResult(
                message_id="fake-message-id",
                recipient=email.to_addresses[0],
                template_type=email.template_type,
                success=True,
            )
        return SendResult(
            message_id="",
            recipient=email.to_addresses[0],
            template_type=email.template_type,
            success=False,
            error="simulated failure",
        )


class TestWelcomeEmailBuilder:
    def test_build_sets_user_name_in_subject(self) -> None:
        email = (
            WelcomeEmailBuilder()
            .set_from("noreply@example.com")
            .set_to("alice@example.com")
            .with_user_name("Alice")
            .build()
        )
        assert "Alice" in email.subject
        assert email.template_type == TemplateType.WELCOME

    def test_build_sets_html_and_text_bodies(self) -> None:
        email = WelcomeEmailBuilder().with_user_name("Bob").build()
        assert "Bob" in email.html_body
        assert "Bob" in email.text_body

    def test_set_to_supports_multiple_recipients(self) -> None:
        email = WelcomeEmailBuilder().set_to("a@example.com", "b@example.com").build()
        assert email.to_addresses == ["a@example.com", "b@example.com"]

    def test_add_attachment_is_stored_on_product(self) -> None:
        attachment = Attachment(filename="logo.png", content=b"binary-data")
        email = WelcomeEmailBuilder().add_attachment(attachment).build()
        assert email.attachments == [attachment]


class TestPasswordResetEmailBuilder:
    def test_build_includes_reset_link(self) -> None:
        email = (
            PasswordResetEmailBuilder()
            .with_reset_link("https://example.com/reset/token123")
            .build()
        )
        assert "https://example.com/reset/token123" in email.html_body
        assert "https://example.com/reset/token123" in email.text_body
        assert email.template_type == TemplateType.PASSWORD_RESET

    def test_build_respects_custom_expiration(self) -> None:
        email = (
            PasswordResetEmailBuilder()
            .with_reset_link("https://example.com/reset", expires_in_hours=1)
            .build()
        )
        assert "1 hours" in email.html_body


class TestOrderConfirmationEmailBuilder:
    def test_build_includes_order_id_and_total(self) -> None:
        items = [{"name": "Widget", "qty": 2, "price": 9.99}]
        email = (
            OrderConfirmationEmailBuilder()
            .with_order_details("ORD-1", items, 19.98)
            .build()
        )
        assert "ORD-1" in email.subject
        assert "19.98" in email.html_body
        assert email.template_type == TemplateType.ORDER_CONFIRMATION

    def test_build_lists_all_items_in_text_body(self) -> None:
        items = [
            {"name": "Widget", "qty": 2, "price": 9.99},
            {"name": "Gadget", "qty": 1, "price": 5.00},
        ]
        email = (
            OrderConfirmationEmailBuilder()
            .with_order_details("ORD-2", items, 24.98)
            .build()
        )
        assert "Widget" in email.text_body
        assert "Gadget" in email.text_body


class TestCampaignDirector:
    def test_build_welcome_uses_default_from_address(self) -> None:
        director = CampaignDirector()
        email = director.build_welcome("alice@example.com", "Alice")
        assert email.from_address == CampaignDirector.DEFAULT_FROM
        assert email.to_addresses == ["alice@example.com"]

    def test_build_password_reset(self) -> None:
        director = CampaignDirector()
        email = director.build_password_reset(
            "bob@example.com", "https://example.com/reset"
        )
        assert email.template_type == TemplateType.PASSWORD_RESET

    def test_build_order_confirmation(self) -> None:
        director = CampaignDirector()
        items = [{"name": "Widget", "qty": 1, "price": 10.0}]
        email = director.build_order_confirmation(
            "carol@example.com", "ORD-3", items, 10.0
        )
        assert email.template_type == TemplateType.ORDER_CONFIRMATION


class TestSendEmailUseCase:
    def test_execute_delegates_to_sender(self) -> None:
        sender = FakeEmailSender()
        builder = WelcomeEmailBuilder().set_to("alice@example.com")
        use_case = SendEmailUseCase(builder, sender)
        email = builder.with_user_name("Alice").build()

        result = use_case.execute(email)

        assert result.success is True
        assert sender.sent_emails == [email]


class TestSendCampaignEmailUseCase:
    def test_send_welcome_returns_success_result(self) -> None:
        sender = FakeEmailSender()
        use_case = SendCampaignEmailUseCase(sender)

        result = use_case.send_welcome("alice@example.com", "Alice")

        assert result.success is True
        assert result.template_type == TemplateType.WELCOME
        assert len(sender.sent_emails) == 1

    def test_send_password_reset_returns_success_result(self) -> None:
        sender = FakeEmailSender()
        use_case = SendCampaignEmailUseCase(sender)

        result = use_case.send_password_reset(
            "bob@example.com", "https://example.com/reset"
        )

        assert result.success is True
        assert result.template_type == TemplateType.PASSWORD_RESET

    def test_send_order_confirmation_returns_success_result(self) -> None:
        sender = FakeEmailSender()
        use_case = SendCampaignEmailUseCase(sender)
        items = [{"name": "Widget", "qty": 1, "price": 10.0}]

        result = use_case.send_order_confirmation(
            "carol@example.com", "ORD-4", items, 10.0
        )

        assert result.success is True
        assert result.template_type == TemplateType.ORDER_CONFIRMATION

    def test_send_welcome_propagates_sender_failure(self) -> None:
        sender = FakeEmailSender(succeed=False)
        use_case = SendCampaignEmailUseCase(sender)

        result = use_case.send_welcome("alice@example.com", "Alice")

        assert result.success is False
        assert result.error == "simulated failure"
