"""Unit tests for PublishEventUseCase, against an in-memory fake publisher."""

from __future__ import annotations

from typing import Any

from cloud_event_notifier.application.use_cases import PublishEventUseCase
from cloud_event_notifier.domain.entities import CloudEvent
from cloud_event_notifier.domain.interfaces import (
    CloudEventObserver,
    CloudEventPublisher,
)


class FakeCloudEventPublisher(CloudEventPublisher):
    def __init__(self) -> None:
        self.published: list[CloudEvent] = []

    def subscribe(self, observer: CloudEventObserver) -> None:
        raise NotImplementedError

    def unsubscribe(self, observer: CloudEventObserver) -> None:
        raise NotImplementedError

    def publish(self, event_type: str, payload: dict[str, Any]) -> CloudEvent:
        event = CloudEvent(event_type=event_type, payload=payload)
        self.published.append(event)
        return event


def test_publish_event_use_case_delegates_to_publisher() -> None:
    publisher = FakeCloudEventPublisher()
    use_case = PublishEventUseCase(publisher)

    event = use_case.execute("order.created", {"order_id": "o1"})

    assert publisher.published == [event]
    assert event.event_type == "order.created"
