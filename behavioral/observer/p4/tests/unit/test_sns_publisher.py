"""Unit tests for SnsCloudEventPublisher using moto."""

from __future__ import annotations

import boto3
from moto import mock_aws

from cloud_event_notifier.infrastructure.observers import EventLogObserver
from cloud_event_notifier.infrastructure.sns_publisher import SnsCloudEventPublisher

TOPIC_NAME = "cloud-events"


def _build_topic() -> tuple[object, str]:
    client = boto3.client("sns", region_name="us-east-1")
    topic_arn = client.create_topic(Name=TOPIC_NAME)["TopicArn"]
    return client, topic_arn


@mock_aws
def test_publish_notifies_local_observers() -> None:
    client, topic_arn = _build_topic()
    publisher = SnsCloudEventPublisher(client, topic_arn)
    observer = EventLogObserver()
    publisher.subscribe(observer)

    event = publisher.publish("order.created", {"order_id": "o1"})

    assert observer.events == [event]


@mock_aws
def test_publish_sends_message_to_sns_topic() -> None:
    client, topic_arn = _build_topic()
    publisher = SnsCloudEventPublisher(client, topic_arn)

    event = publisher.publish("order.created", {"order_id": "o1"})

    assert event.event_type == "order.created"
    assert event.payload == {"order_id": "o1"}


@mock_aws
def test_unsubscribe_stops_observer_from_receiving_events() -> None:
    client, topic_arn = _build_topic()
    publisher = SnsCloudEventPublisher(client, topic_arn)
    observer = EventLogObserver()
    publisher.subscribe(observer)
    publisher.unsubscribe(observer)

    publisher.publish("order.created", {})

    assert observer.events == []


@mock_aws
def test_unsubscribe_unknown_observer_is_a_no_op() -> None:
    client, topic_arn = _build_topic()
    publisher = SnsCloudEventPublisher(client, topic_arn)
    observer = EventLogObserver()

    publisher.unsubscribe(observer)  # should not raise


@mock_aws
def test_multiple_observers_all_receive_the_same_event() -> None:
    client, topic_arn = _build_topic()
    publisher = SnsCloudEventPublisher(client, topic_arn)
    first = EventLogObserver()
    second = EventLogObserver()
    publisher.subscribe(first)
    publisher.subscribe(second)

    event = publisher.publish("order.created", {})

    assert first.events == [event]
    assert second.events == [event]
