"""Application use cases for the Live Dashboard.

Each use case has a single responsibility and depends only on the
MetricsPublisher abstraction (DIP).
"""

from __future__ import annotations

from live_dashboard_observer.domain.entities import MetricEvent
from live_dashboard_observer.domain.interfaces import MetricsPublisher
from live_dashboard_observer.infrastructure.observers import DashboardStateObserver


class PublishMetricUseCase:
    """Publishes a metric update, fanning out to local observers and Pub/Sub."""

    def __init__(self, publisher: MetricsPublisher) -> None:
        self._publisher = publisher

    def execute(self, metric_name: str, value: float) -> MetricEvent:
        return self._publisher.publish(metric_name, value)


class GetDashboardStateUseCase:
    """Returns the latest known value of every metric."""

    def __init__(self, state_observer: DashboardStateObserver) -> None:
        self._state_observer = state_observer

    def execute(self) -> dict[str, MetricEvent]:
        return self._state_observer.latest_values
