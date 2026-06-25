"""Observer pattern interfaces for the Cloud Event Notifier.

Defines the Subject (CloudEventPublisher) and Observer (CloudEventObserver)
ABCs. Concrete subjects decide HOW to distribute events (in-process,
AWS SNS, etc.) while this interface stays stable.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from cloud_event_notifier.domain.entities import CloudEvent


class CloudEventObserver(ABC):
    """Abstract base for all local (in-process) cloud event observers.

    OCP: new observer types extend this without modifying CloudEventPublisher.
    DIP: CloudEventPublisher depends on this abstraction, not concrete classes.
    """

    @abstractmethod
    def on_cloud_event(self, event: CloudEvent) -> None:
        """React to a cloud event right after it is published."""
        ...


class CloudEventPublisher(ABC):
    """Subject ABC — maintains local observers and drives notifications,
    in addition to publishing each event to the remote cloud channel."""

    @abstractmethod
    def subscribe(self, observer: CloudEventObserver) -> None:
        """Register a local observer to receive every future event."""
        ...

    @abstractmethod
    def unsubscribe(self, observer: CloudEventObserver) -> None:
        """Remove a previously registered local observer."""
        ...

    @abstractmethod
    def publish(self, event_type: str, payload: dict[str, Any]) -> CloudEvent:
        """Build a CloudEvent, notify local observers, and push it to the
        remote cloud channel."""
        ...
