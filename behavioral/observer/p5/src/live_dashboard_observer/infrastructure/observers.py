"""ConcreteObservers reacting to locally published MetricEvents.

OCP: a new local reaction is added by writing a new class implementing
MetricsObserver and subscribing it, without touching PubSubMetricsPublisher.
"""

from __future__ import annotations

from live_dashboard_observer.domain.entities import MetricEvent
from live_dashboard_observer.domain.interfaces import MetricsObserver


class DashboardStateObserver(MetricsObserver):
    """Keeps the latest value of every metric in memory, for the
    Streamlit dashboard to render. SRP: only tracks state, renders nothing."""

    def __init__(self) -> None:
        self._latest: dict[str, MetricEvent] = {}

    def on_metric_event(self, event: MetricEvent) -> None:
        self._latest[event.metric_name] = event

    @property
    def latest_values(self) -> dict[str, MetricEvent]:
        return dict(self._latest)


class EventLogObserver(MetricsObserver):
    """Keeps every published event in memory — useful for tests and for
    any caller that wants to inspect what was fanned out locally."""

    def __init__(self) -> None:
        self.events: list[MetricEvent] = []

    def on_metric_event(self, event: MetricEvent) -> None:
        self.events.append(event)
