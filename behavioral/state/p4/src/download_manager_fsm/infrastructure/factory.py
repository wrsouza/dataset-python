"""Composition helpers — builds the concrete SQLite connection and S3 client."""

from __future__ import annotations

import os
import sqlite3
from typing import Protocol, cast


class S3ClientLike(Protocol):
    """Minimal boto3 S3 client contract this app relies on."""

    def head_object(self, Bucket: str, Key: str) -> dict[str, object]: ...


def build_connection() -> sqlite3.Connection:
    path = os.environ.get("DOWNLOAD_MANAGER_DB_PATH", "download_manager.db")
    return sqlite3.connect(path)


def build_s3_client() -> S3ClientLike:
    import boto3

    client = boto3.client(
        "s3",
        endpoint_url=os.environ.get("S3_ENDPOINT_URL") or None,
        region_name=os.environ.get("AWS_REGION", "us-east-1"),
    )
    return cast(S3ClientLike, client)
