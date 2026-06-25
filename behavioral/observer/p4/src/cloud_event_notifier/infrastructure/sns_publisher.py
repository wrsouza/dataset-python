"""ConcreteSubject: publishes CloudEvents to a local observer list and
to an AWS SNS topic.

The local observers are notified synchronously and unconditionally —
they always run, even if SNS is unreachable — so logging/auditing
never depends on the cloud round-trip succeeding.
"""

from __future__ import annotations

import json
from typing import Any, Protocol

from cloud_event_notifier.domain.entities import CloudEvent
from cloud_event_notifier.domain.interfaces import (
    CloudEventObserver,
    CloudEventPublisher,
)


class SNSClientLike(Protocol):
    """Minimal boto3 SNS client contract this publisher relies on."""

    def publish(self, TopicArn: str, Message: str) -> dict[str, Any]: ...


class SnsCloudEventPublisher(CloudEventPublisher):
    """Fans out to local observers, then publishes to an AWS SNS topic."""

    def __init__(self, client: SNSClientLike, topic_arn: str) -> None:
        self._client = client
        self._topic_arn = topic_arn
        self._observers: list[CloudEventObserver] = []

    def subscribe(self, observer: CloudEventObserver) -> None:
        self._observers.append(observer)

    def unsubscribe(self, observer: CloudEventObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def publish(self, event_type: str, payload: dict[str, Any]) -> CloudEvent:
        event = CloudEvent(event_type=event_type, payload=payload)
        for observer in self._observers:
            observer.on_cloud_event(event)

        message = json.dumps(
            {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "payload": event.payload,
                "occurred_at": event.occurred_at.isoformat(),
            }
        )
        self._client.publish(TopicArn=self._topic_arn, Message=message)
        return event
