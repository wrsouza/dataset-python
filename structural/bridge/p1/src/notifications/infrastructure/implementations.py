"""Concrete Implementations — delivery channels.

Each sender knows HOW to deliver; it is unaware of notification types.
EmailSender uses LocalStack SES; SMS and Push use structured logging
to simulate real providers without external dependencies.
"""
from __future__ import annotations

import logging
import uuid

import boto3
from botocore.exceptions import ClientError

from notifications.domain.entities import Channel, DeliveryResult, DeliveryStatus
from notifications.domain.interfaces import NotificationSender

logger = logging.getLogger(__name__)


class EmailSender(NotificationSender):
    """Delivers via AWS SES (LocalStack in dev, real SES in prod)."""

    def __init__(
        self,
        sender_address: str,
        ses_client: object | None = None,
        endpoint_url: str | None = None,
        region: str = "us-east-1",
    ) -> None:
        self._from = sender_address
        # Allow injection of a pre-configured client for testing.
        self._ses = ses_client or boto3.client(
            "ses",
            region_name=region,
            endpoint_url=endpoint_url,
        )

    def deliver(self, to: str, subject: str, body: str) -> DeliveryResult:
        try:
            response = self._ses.send_email(
                Source=self._from,
                Destination={"ToAddresses": [to]},
                Message={
                    "Subject": {"Data": subject},
                    "Body": {"Text": {"Data": body}},
                },
            )
            message_id: str = response["MessageId"]
            logger.info("Email sent to %s, message_id=%s", to, message_id)
            return DeliveryResult(
                status=DeliveryStatus.SENT,
                message_id=message_id,
                channel=Channel.EMAIL,
            )
        except ClientError as exc:
            error_msg = exc.response["Error"]["Message"]
            logger.error("SES delivery failed: %s", error_msg)
            return DeliveryResult(
                status=DeliveryStatus.FAILED,
                message_id="",
                channel=Channel.EMAIL,
                error=error_msg,
            )


class SMSSender(NotificationSender):
    """Simulates SMS delivery via structured logging (swap for Twilio/SNS)."""

    def deliver(self, to: str, subject: str, body: str) -> DeliveryResult:
        message_id = f"sms-{uuid.uuid4().hex[:12]}"
        # SMS body is typically subject + truncated body.
        sms_text = f"{subject}: {body[:140]}"
        logger.info(
            "SMS delivered",
            extra={
                "message_id": message_id,
                "to": to,
                "text": sms_text,
                "channel": "sms",
            },
        )
        return DeliveryResult(
            status=DeliveryStatus.SENT,
            message_id=message_id,
            channel=Channel.SMS,
        )


class PushSender(NotificationSender):
    """Simulates push notification via structured logging (swap for FCM/APNs)."""

    def deliver(self, to: str, subject: str, body: str) -> DeliveryResult:
        message_id = f"push-{uuid.uuid4().hex[:12]}"
        logger.info(
            "Push notification delivered",
            extra={
                "message_id": message_id,
                "device_token": to,
                "title": subject,
                "body": body[:256],
                "channel": "push",
            },
        )
        return DeliveryResult(
            status=DeliveryStatus.SENT,
            message_id=message_id,
            channel=Channel.PUSH,
        )
