"""Composition helpers for wiring exports to a real S3 client."""

from __future__ import annotations

import os
from typing import Protocol, cast


class S3ClientLike(Protocol):
    """Minimal boto3 S3 client contract this app relies on."""

    def put_object(self, Bucket: str, Key: str, Body: bytes) -> dict[str, object]: ...


def build_s3_client() -> S3ClientLike:
    import boto3

    client = boto3.client(
        "s3",
        endpoint_url=os.environ.get("S3_ENDPOINT_URL") or None,
        region_name=os.environ.get("AWS_REGION", "us-east-1"),
    )
    return cast(S3ClientLike, client)
