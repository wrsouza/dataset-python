"""ConcreteSubject: publishes MetricEvents to local observers and to a
GCP Pub/Sub topic.

Local observers are notified synchronously and unconditionally — they
always run, even if Pub/Sub is unreachable — so the dashboard's own
state update never depends on the cloud round-trip succeeding.
"""

from __future__ import annotations

import json
from typing import Protocol

from live_dashboard_observer.domain.entities import MetricEvent
from live_dashboard_observer.domain.interfaces import MetricsObserver, MetricsPublisher


class PubSubClientLike(Protocol):
    """Minimal google-cloud-pubsub PublisherClient contract this
    publisher relies on."""

    def publish(self, topic: str, data: bytes) -> object: ...


class PubSubMetricsPublisher(MetricsPublisher):
    """Fans out to local observers, then publishes to a GCP Pub/Sub topic."""

    def __init__(self, client: PubSubClientLike, topic_path: str) -> None:
        self._client = client
        self._topic_path = topic_path
        self._observers: list[MetricsObserver] = []

    def subscribe(self, observer: MetricsObserver) -> None:
        self._observers.append(observer)

    def unsubscribe(self, observer: MetricsObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def publish(self, metric_name: str, value: float) -> MetricEvent:
        event = MetricEvent(metric_name=metric_name, value=value)
        for observer in self._observers:
            observer.on_metric_event(event)

        data = json.dumps(
            {
                "metric_name": event.metric_name,
                "value": event.value,
                "occurred_at": event.occurred_at.isoformat(),
            }
        ).encode("utf-8")
        self._client.publish(self._topic_path, data=data)
        return event
