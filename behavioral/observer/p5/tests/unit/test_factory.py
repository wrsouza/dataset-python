"""Unit tests for the Pub/Sub client/publisher factory helpers.

`google.cloud.pubsub_v1.PublisherClient()` requires real GCP
credentials to construct, so `build_client` is monkeypatched with a
stand-in class — the same approach used for the moto-less GCP fakes
elsewhere in this project.
"""

from __future__ import annotations

import pytest

from live_dashboard_observer.infrastructure import factory
from live_dashboard_observer.infrastructure.pubsub_publisher import (
    PubSubMetricsPublisher,
)


class FakePublisherClient:
    def publish(self, topic: str, data: bytes) -> object:
        return object()


def test_build_publisher_uses_env_vars_for_topic_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(factory, "build_client", lambda: FakePublisherClient())
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "my-project")
    monkeypatch.setenv("PUBSUB_TOPIC_ID", "my-topic")

    publisher = factory.build_publisher()

    assert isinstance(publisher, PubSubMetricsPublisher)
    assert (
        publisher._topic_path == "projects/my-project/topics/my-topic"
    )  # noqa: SLF001


def test_build_publisher_defaults_when_env_vars_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(factory, "build_client", lambda: FakePublisherClient())
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    monkeypatch.delenv("PUBSUB_TOPIC_ID", raising=False)

    publisher = factory.build_publisher()

    assert (
        publisher._topic_path == "projects/demo-project/topics/dashboard-metrics"
    )  # noqa: SLF001
