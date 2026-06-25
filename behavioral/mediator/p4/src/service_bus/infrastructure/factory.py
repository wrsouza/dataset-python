"""Composition helpers for wiring the mediator to a real SQS queue."""

from __future__ import annotations

import os
from typing import cast

import boto3

from service_bus.infrastructure.sqs_service_bus import (
    SQSClientLike,
    SqsServiceBusMediator,
)


def build_client() -> SQSClientLike:
    """Build a boto3 SQS client, pointing at LocalStack in dev if configured."""
    client = boto3.client(
        "sqs",
        endpoint_url=os.environ.get("SQS_ENDPOINT_URL") or None,
        region_name=os.environ.get("AWS_REGION", "us-east-1"),
    )
    return cast(SQSClientLike, client)


def build_mediator() -> SqsServiceBusMediator:
    """Build the service bus mediator for the configured queue URL."""
    queue_url = os.environ["SQS_QUEUE_URL"]
    return SqsServiceBusMediator(build_client(), queue_url)
