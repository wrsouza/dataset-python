"""Application use cases for the Cloud Event Notifier.

The single use case has one responsibility and depends only on the
CloudEventPublisher abstraction (DIP).
"""

from __future__ import annotations

from typing import Any

from cloud_event_notifier.domain.entities import CloudEvent
from cloud_event_notifier.domain.interfaces import CloudEventPublisher


class PublishEventUseCase:
    """Publishes a cloud event, fanning out to local observers and SNS."""

    def __init__(self, publisher: CloudEventPublisher) -> None:
        self._publisher = publisher

    def execute(self, event_type: str, payload: dict[str, Any]) -> CloudEvent:
        return self._publisher.publish(event_type, payload)
