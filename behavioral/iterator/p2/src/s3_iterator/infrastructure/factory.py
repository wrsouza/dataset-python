"""Composition helpers for wiring the source to a real S3 (or LocalStack) bucket."""

from __future__ import annotations

import os
from typing import cast

import boto3

from s3_iterator.infrastructure.s3_source import BotoS3ObjectSource, S3ClientLike


def build_client() -> S3ClientLike:
    """Build a boto3 S3 client, pointing at LocalStack in dev if configured."""
    client = boto3.client(
        "s3",
        endpoint_url=os.environ.get("S3_ENDPOINT_URL") or None,
        region_name=os.environ.get("AWS_REGION", "us-east-1"),
    )
    return cast(S3ClientLike, client)


def build_source() -> BotoS3ObjectSource:
    """Build the object source for the configured bucket."""
    bucket = os.environ.get("S3_BUCKET", "iterator-demo-bucket")
    return BotoS3ObjectSource(build_client(), bucket)
