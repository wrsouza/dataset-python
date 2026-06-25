"""Unit tests for SqsServiceBusMediator using moto."""

from __future__ import annotations

import boto3
from moto import mock_aws

from service_bus.infrastructure.sqs_service_bus import SqsServiceBusMediator

QUEUE_NAME = "test-queue"


def _build_queue() -> tuple[object, str]:
    client = boto3.client("sqs", region_name="us-east-1")
    queue_url = client.create_queue(QueueName=QUEUE_NAME)["QueueUrl"]
    return client, queue_url


@mock_aws
def test_send_places_a_message_on_the_queue() -> None:
    client, queue_url = _build_queue()
    mediator = SqsServiceBusMediator(client, queue_url)

    message = mediator.send("billing-service", {"invoice_id": "i-1"})

    assert message.sender_service == "billing-service"
    assert message.payload == {"invoice_id": "i-1"}


@mock_aws
def test_receive_returns_sent_message_and_removes_it() -> None:
    client, queue_url = _build_queue()
    mediator = SqsServiceBusMediator(client, queue_url)
    mediator.send("billing-service", {"invoice_id": "i-1"})

    [received] = mediator.receive(max_messages=10)

    assert received.sender_service == "billing-service"
    assert received.payload == {"invoice_id": "i-1"}
    assert mediator.receive(max_messages=10) == []


@mock_aws
def test_receive_returns_empty_list_for_empty_queue() -> None:
    client, queue_url = _build_queue()
    mediator = SqsServiceBusMediator(client, queue_url)

    assert mediator.receive(max_messages=10) == []


@mock_aws
def test_receive_respects_max_messages() -> None:
    client, queue_url = _build_queue()
    mediator = SqsServiceBusMediator(client, queue_url)
    mediator.send("a", {"n": 1})
    mediator.send("b", {"n": 2})
    mediator.send("c", {"n": 3})

    received = mediator.receive(max_messages=2)

    assert len(received) <= 2
