"""Observer pattern interfaces for the Live Dashboard.

Defines the Subject (MetricsPublisher) and Observer (MetricsObserver)
ABCs. Concrete subjects decide HOW to distribute events (in-process,
GCP Pub/Sub, etc.) while this interface stays stable.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from live_dashboard_observer.domain.entities import MetricEvent


class MetricsObserver(ABC):
    """Abstract base for all local (in-process) metric observers.

    OCP: new observer types extend this without modifying MetricsPublisher.
    DIP: MetricsPublisher depends on this abstraction, not concrete classes.
    """

    @abstractmethod
    def on_metric_event(self, event: MetricEvent) -> None:
        """React to a metric update right after it is published."""
        ...


class MetricsPublisher(ABC):
    """Subject ABC — maintains local observers and drives notifications,
    in addition to publishing each event to the remote Pub/Sub topic."""

    @abstractmethod
    def subscribe(self, observer: MetricsObserver) -> None:
        """Register a local observer to receive every future event."""
        ...

    @abstractmethod
    def unsubscribe(self, observer: MetricsObserver) -> None:
        """Remove a previously registered local observer."""
        ...

    @abstractmethod
    def publish(self, metric_name: str, value: float) -> MetricEvent:
        """Build a MetricEvent, notify local observers, and push it to
        the remote Pub/Sub topic."""
        ...
