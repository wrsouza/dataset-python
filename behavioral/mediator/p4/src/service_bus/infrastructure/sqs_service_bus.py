"""AWS SQS-backed implementation of ServiceBusMediator."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Protocol

from service_bus.domain.entities import ServiceMessage
from service_bus.domain.interfaces import ServiceBusMediator


class SQSClientLike(Protocol):
    """Minimal boto3 SQS client contract this mediator relies on."""

    def send_message(self, QueueUrl: str, MessageBody: str) -> dict[str, Any]: ...

    def receive_message(
        self, QueueUrl: str, MaxNumberOfMessages: int
    ) -> dict[str, Any]: ...

    def delete_message(self, QueueUrl: str, ReceiptHandle: str) -> object: ...


class SqsServiceBusMediator(ServiceBusMediator):
    """Routes ServiceMessages between services through a single SQS queue."""

    def __init__(self, client: SQSClientLike, queue_url: str) -> None:
        self._client = client
        self._queue_url = queue_url

    def send(self, sender_service: str, payload: dict[str, object]) -> ServiceMessage:
        message = ServiceMessage(sender_service=sender_service, payload=payload)
        body = json.dumps(
            {
                "sender_service": message.sender_service,
                "payload": message.payload,
                "sent_at": message.sent_at.isoformat(),
            }
        )
        self._client.send_message(QueueUrl=self._queue_url, MessageBody=body)
        return message

    def receive(self, max_messages: int) -> list[ServiceMessage]:
        response = self._client.receive_message(
            QueueUrl=self._queue_url, MaxNumberOfMessages=max_messages
        )
        messages = []
        for raw in response.get("Messages", []):
            data = json.loads(raw["Body"])
            messages.append(
                ServiceMessage(
                    sender_service=data["sender_service"],
                    payload=data["payload"],
                    sent_at=datetime.fromisoformat(data["sent_at"]),
                    receipt_handle=raw["ReceiptHandle"],
                )
            )
            self._client.delete_message(
                QueueUrl=self._queue_url, ReceiptHandle=raw["ReceiptHandle"]
            )
        return messages
