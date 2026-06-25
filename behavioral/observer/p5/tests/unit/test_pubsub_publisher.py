"""Unit tests for PubSubMetricsPublisher, against a fake Pub/Sub client.

There is no GCP equivalent of moto, so the publisher is tested against
a minimal in-memory fake implementing PubSubClientLike — the same
approach as the Redis/RabbitMQ fakes used elsewhere in this dataset.
"""

from __future__ import annotations

from live_dashboard_observer.infrastructure.observers import EventLogObserver
from live_dashboard_observer.infrastructure.pubsub_publisher import (
    PubSubMetricsPublisher,
)

TOPIC_PATH = "projects/demo-project/topics/dashboard-metrics"


class FakePubSubClient:
    def __init__(self) -> None:
        self.published: list[tuple[str, bytes]] = []

    def publish(self, topic: str, data: bytes) -> object:
        self.published.append((topic, data))
        return object()


def test_publish_notifies_local_observers() -> None:
    client = FakePubSubClient()
    publisher = PubSubMetricsPublisher(client, TOPIC_PATH)
    observer = EventLogObserver()
    publisher.subscribe(observer)

    event = publisher.publish("cpu_usage", 42.0)

    assert observer.events == [event]


def test_publish_sends_message_to_pubsub_topic() -> None:
    client = FakePubSubClient()
    publisher = PubSubMetricsPublisher(client, TOPIC_PATH)

    publisher.publish("cpu_usage", 42.0)

    assert len(client.published) == 1
    topic, data = client.published[0]
    assert topic == TOPIC_PATH
    assert b"cpu_usage" in data


def test_unsubscribe_stops_observer_from_receiving_events() -> None:
    client = FakePubSubClient()
    publisher = PubSubMetricsPublisher(client, TOPIC_PATH)
    observer = EventLogObserver()
    publisher.subscribe(observer)
    publisher.unsubscribe(observer)

    publisher.publish("cpu_usage", 1.0)

    assert observer.events == []


def test_unsubscribe_unknown_observer_is_a_no_op() -> None:
    client = FakePubSubClient()
    publisher = PubSubMetricsPublisher(client, TOPIC_PATH)
    observer = EventLogObserver()

    publisher.unsubscribe(observer)  # should not raise


def test_multiple_observers_all_receive_the_same_event() -> None:
    client = FakePubSubClient()
    publisher = PubSubMetricsPublisher(client, TOPIC_PATH)
    first = EventLogObserver()
    second = EventLogObserver()
    publisher.subscribe(first)
    publisher.subscribe(second)

    event = publisher.publish("cpu_usage", 1.0)

    assert first.events == [event]
    assert second.events == [event]
