"""Composition helpers for wiring the publisher to a real SNS topic."""

from __future__ import annotations

import os
from typing import cast

import boto3

from cloud_event_notifier.infrastructure.sns_publisher import (
    SNSClientLike,
    SnsCloudEventPublisher,
)


def build_client() -> SNSClientLike:
    """Build a boto3 SNS client, pointing at LocalStack in dev if configured."""
    client = boto3.client(
        "sns",
        endpoint_url=os.environ.get("SNS_ENDPOINT_URL") or None,
        region_name=os.environ.get("AWS_REGION", "us-east-1"),
    )
    return cast(SNSClientLike, client)


def build_publisher() -> SnsCloudEventPublisher:
    """Build the cloud event publisher for the configured SNS topic."""
    topic_arn = os.environ["SNS_TOPIC_ARN"]
    return SnsCloudEventPublisher(build_client(), topic_arn)
