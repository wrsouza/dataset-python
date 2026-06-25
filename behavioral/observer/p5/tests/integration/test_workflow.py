"""Integration-style test exercising publish -> dashboard state, mirroring
how the Streamlit app wires the publisher and observer together."""

from __future__ import annotations

from live_dashboard_observer.application.use_cases import (
    GetDashboardStateUseCase,
    PublishMetricUseCase,
)
from live_dashboard_observer.infrastructure.observers import DashboardStateObserver
from live_dashboard_observer.infrastructure.pubsub_publisher import (
    PubSubMetricsPublisher,
)


class FakePubSubClient:
    def __init__(self) -> None:
        self.published: list[tuple[str, bytes]] = []

    def publish(self, topic: str, data: bytes) -> object:
        self.published.append((topic, data))
        return object()


def test_full_publish_to_dashboard_state_workflow() -> None:
    client = FakePubSubClient()
    publisher = PubSubMetricsPublisher(
        client, "projects/demo-project/topics/dashboard-metrics"
    )
    state_observer = DashboardStateObserver()
    publisher.subscribe(state_observer)

    PublishMetricUseCase(publisher).execute("cpu_usage", 10.0)
    PublishMetricUseCase(publisher).execute("active_users", 3.0)
    PublishMetricUseCase(publisher).execute("cpu_usage", 25.0)

    state = GetDashboardStateUseCase(state_observer).execute()
    assert state["cpu_usage"].value == 25.0
    assert state["active_users"].value == 3.0
    assert len(client.published) == 3
