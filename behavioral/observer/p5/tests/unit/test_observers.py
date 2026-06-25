"""Unit tests for DashboardStateObserver and EventLogObserver."""

from __future__ import annotations

from live_dashboard_observer.domain.entities import MetricEvent
from live_dashboard_observer.infrastructure.observers import (
    DashboardStateObserver,
    EventLogObserver,
)


def test_dashboard_state_observer_tracks_latest_value_per_metric() -> None:
    observer = DashboardStateObserver()

    observer.on_metric_event(MetricEvent(metric_name="cpu_usage", value=10.0))
    observer.on_metric_event(MetricEvent(metric_name="cpu_usage", value=20.0))
    observer.on_metric_event(MetricEvent(metric_name="active_users", value=5.0))

    state = observer.latest_values
    assert state["cpu_usage"].value == 20.0
    assert state["active_users"].value == 5.0


def test_event_log_observer_records_every_event() -> None:
    observer = EventLogObserver()
    first = MetricEvent(metric_name="cpu_usage", value=10.0)
    second = MetricEvent(metric_name="cpu_usage", value=20.0)

    observer.on_metric_event(first)
    observer.on_metric_event(second)

    assert observer.events == [first, second]
