"""Integration tests — EmailSender against LocalStack SES.

Run with: docker-compose run --rm app pytest tests/integration/ -v
Requires: localstack service healthy and SES email verified.
"""
from __future__ import annotations

import os

import boto3
import pytest

from notifications.domain.entities import Channel, DeliveryStatus
from notifications.infrastructure.implementations import EmailSender

LOCALSTACK_ENDPOINT = os.getenv("LOCALSTACK_ENDPOINT", "http://localstack:4566")
SENDER_EMAIL = os.getenv("SES_SENDER", "noreply@example.com")


@pytest.fixture(scope="module")
def ses_client() -> object:
    return boto3.client(
        "ses",
        region_name="us-east-1",
        endpoint_url=LOCALSTACK_ENDPOINT,
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )


@pytest.fixture(scope="module", autouse=True)
def verify_email(ses_client: object) -> None:
    """LocalStack SES requires email verification before sending."""
    ses_client.verify_email_identity(EmailAddress=SENDER_EMAIL)
    ses_client.verify_email_identity(EmailAddress="recipient@example.com")


@pytest.mark.integration
def test_email_sender_delivers_successfully(ses_client: object) -> None:
    sender = EmailSender(
        sender_address=SENDER_EMAIL,
        ses_client=ses_client,
    )
    result = sender.deliver(
        to="recipient@example.com",
        subject="Integration Test",
        body="This is an integration test via LocalStack SES.",
    )
    assert result.status == DeliveryStatus.SENT
    assert result.channel == Channel.EMAIL
    assert result.message_id != ""
