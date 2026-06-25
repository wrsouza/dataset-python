"""AWS SES email sender — connects to LocalStack in dev."""

from __future__ import annotations

import boto3
from botocore.exceptions import ClientError

from email_builder.domain.entities import Email, SendResult


class SESEmailSender:
    """Infrastructure adapter: sends Email via AWS SES (or LocalStack).

    DIP: implements EmailSender protocol — use cases don't import boto3.
    """

    def __init__(
        self, endpoint_url: str | None = None, region: str = "us-east-1"
    ) -> None:
        self._client = boto3.client(
            "ses",
            region_name=region,
            endpoint_url=endpoint_url,
            aws_access_key_id="test",  # noqa: S106 — fixed test creds for LocalStack
            aws_secret_access_key="test",  # noqa: S106
        )

    def send(self, email: Email) -> SendResult:
        try:
            response = self._client.send_email(
                Source=email.from_address,
                Destination={"ToAddresses": email.to_addresses},
                Message={
                    "Subject": {"Data": email.subject},
                    "Body": {
                        "Html": {"Data": email.html_body},
                        "Text": {"Data": email.text_body},
                    },
                },
            )
            return SendResult(
                message_id=response["MessageId"],
                recipient=email.to_addresses[0],
                template_type=email.template_type,
                success=True,
            )
        except ClientError as exc:
            return SendResult(
                message_id="",
                recipient=email.to_addresses[0] if email.to_addresses else "",
                template_type=email.template_type,
                success=False,
                error=str(exc),
            )
