"""Unit tests for the Live Dashboard use cases."""

from __future__ import annotations

from live_dashboard_observer.application.use_cases import (
    GetDashboardStateUseCase,
    PublishMetricUseCase,
)
from live_dashboard_observer.domain.entities import MetricEvent
from live_dashboard_observer.domain.interfaces import MetricsObserver, MetricsPublisher
from live_dashboard_observer.infrastructure.observers import DashboardStateObserver


class FakeMetricsPublisher(MetricsPublisher):
    def __init__(self) -> None:
        self.published: list[MetricEvent] = []
        self._observers: list[MetricsObserver] = []

    def subscribe(self, observer: MetricsObserver) -> None:
        self._observers.append(observer)

    def unsubscribe(self, observer: MetricsObserver) -> None:
        self._observers.remove(observer)

    def publish(self, metric_name: str, value: float) -> MetricEvent:
        event = MetricEvent(metric_name=metric_name, value=value)
        for observer in self._observers:
            observer.on_metric_event(event)
        self.published.append(event)
        return event


def test_publish_metric_use_case_delegates_to_publisher() -> None:
    publisher = FakeMetricsPublisher()
    use_case = PublishMetricUseCase(publisher)

    event = use_case.execute("cpu_usage", 42.0)

    assert publisher.published == [event]


def test_get_dashboard_state_use_case_reflects_published_metrics() -> None:
    publisher = FakeMetricsPublisher()
    state_observer = DashboardStateObserver()
    publisher.subscribe(state_observer)

    PublishMetricUseCase(publisher).execute("cpu_usage", 42.0)

    state = GetDashboardStateUseCase(state_observer).execute()
    assert state["cpu_usage"].value == 42.0
