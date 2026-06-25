from __future__ import annotations

import json
import logging

import boto3
from botocore.config import Config

from src.order.domain.entities import Customer, Order, ShippingLabel

logger = logging.getLogger(__name__)


class SQSNotificationService:
    """
    Sends order notifications via AWS SQS (LocalStack in development).

    Uses fire-and-forget: failures are logged but do not abort the order.
    """

    def __init__(self, queue_url: str, endpoint_url: str | None = None) -> None:
        self._queue_url = queue_url
        self._client = boto3.client(
            "sqs",
            region_name="us-east-1",
            endpoint_url=endpoint_url,
            config=Config(retries={"max_attempts": 3, "mode": "standard"}),
        )

    def send_order_confirmation(
        self,
        order: Order,
        customer: Customer,
        label: ShippingLabel,
    ) -> None:
        message = {
            "type": "ORDER_CONFIRMED",
            "order_id": order.id,
            "customer_email": customer.email,
            "customer_name": customer.name,
            "tracking_number": label.tracking_number,
            "carrier": label.carrier,
            "estimated_days": label.estimated_days,
            "total_amount": order.total_amount,
        }
        self._send_message(message)
        logger.info("Confirmation notification queued for order %s", order.id)

    def send_order_failure(self, order: Order, customer: Customer) -> None:
        message = {
            "type": "ORDER_FAILED",
            "order_id": order.id,
            "customer_email": customer.email,
            "customer_name": customer.name,
            "reason": "Payment could not be processed",
        }
        self._send_message(message)
        logger.info("Failure notification queued for order %s", order.id)

    def _send_message(self, message: dict) -> None:  # type: ignore[type-arg]
        self._client.send_message(
            QueueUrl=self._queue_url,
            MessageBody=json.dumps(message),
        )
