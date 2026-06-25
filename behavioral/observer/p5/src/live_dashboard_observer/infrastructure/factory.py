"""Composition helpers for wiring the publisher to a real Pub/Sub topic."""

from __future__ import annotations

import os
from typing import cast

from google.cloud import pubsub_v1

from live_dashboard_observer.infrastructure.pubsub_publisher import (
    PubSubClientLike,
    PubSubMetricsPublisher,
)


def build_client() -> PubSubClientLike:
    """Build a real google-cloud-pubsub PublisherClient."""
    return cast(PubSubClientLike, pubsub_v1.PublisherClient())


def build_publisher() -> PubSubMetricsPublisher:
    """Build the metrics publisher for the configured Pub/Sub topic."""
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "demo-project")
    topic_id = os.environ.get("PUBSUB_TOPIC_ID", "dashboard-metrics")
    topic_path = f"projects/{project_id}/topics/{topic_id}"
    return PubSubMetricsPublisher(build_client(), topic_path)
