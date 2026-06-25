"""Unit tests for the SES infrastructure adapter — mocked via moto."""

from __future__ import annotations

import boto3
import pytest
from moto import mock_aws

from email_builder.domain.entities import Email, TemplateType
from email_builder.infrastructure.ses_sender import SESEmailSender

VERIFIED_SENDER = "noreply@example.com"


@pytest.fixture
def verified_ses_sender():  # type: ignore[no-untyped-def]
    with mock_aws():
        client = boto3.client(
            "ses",
            region_name="us-east-1",
            aws_access_key_id="test",  # noqa: S106
            aws_secret_access_key="test",  # noqa: S106
        )
        client.verify_email_identity(EmailAddress=VERIFIED_SENDER)
        sender = SESEmailSender(endpoint_url=None, region="us-east-1")
        yield sender


class TestSESEmailSender:
    def test_send_returns_success_result(
        self, verified_ses_sender: SESEmailSender
    ) -> None:
        email = Email(
            subject="Hello",
            from_address=VERIFIED_SENDER,
            to_addresses=["alice@example.com"],
            html_body="<p>Hi</p>",
            text_body="Hi",
            template_type=TemplateType.WELCOME,
        )

        result = verified_ses_sender.send(email)

        assert result.success is True
        assert result.message_id
        assert result.recipient == "alice@example.com"

    def test_send_with_unverified_sender_returns_failure(
        self, verified_ses_sender: SESEmailSender
    ) -> None:
        email = Email(
            subject="Hello",
            from_address="not-verified@example.com",
            to_addresses=["bob@example.com"],
            html_body="<p>Hi</p>",
            text_body="Hi",
            template_type=TemplateType.PASSWORD_RESET,
        )

        result = verified_ses_sender.send(email)

        assert result.success is False
        assert result.error is not None
        assert result.recipient == "bob@example.com"
