"""S3 storage client wrapping boto3 — adapts AWS API to domain FSNode objects."""

from __future__ import annotations

import os
from datetime import datetime
from typing import TYPE_CHECKING

import boto3
from botocore.exceptions import ClientError

from filesystem.domain.exceptions import FSNodeNotFoundError, FSStorageError
from filesystem.domain.interfaces import FSNode

if TYPE_CHECKING:
    from mypy_boto3_s3.client import S3Client

BUCKET_NAME = os.getenv("S3_BUCKET", "vfs-bucket")
AWS_ENDPOINT = os.getenv("AWS_ENDPOINT_URL", "http://localstack:4566")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")


class S3StorageClient:
    """Infrastructure adapter: translates S3 objects into FSNode trees.

    SRP: only handles S3 communication and FSNode construction.
    DIP: use cases depend on this via constructor injection.
    """

    def __init__(
        self, s3_client: S3Client | None = None, bucket: str | None = None
    ) -> None:
        self._s3: S3Client = s3_client or boto3.client(
            "s3",
            endpoint_url=AWS_ENDPOINT,
            region_name=AWS_REGION,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
        )
        self._bucket = bucket or BUCKET_NAME
        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        try:
            self._s3.head_bucket(Bucket=self._bucket)
        except ClientError:
            self._s3.create_bucket(Bucket=self._bucket)

    def get_node(self, path: str) -> FSNode:
        """Return a FSNode for the given path (file or folder)."""
        from filesystem.domain.entities import Directory, File  # noqa: PLC0415

        # Check if path is an exact file key
        try:
            head = self._s3.head_object(Bucket=self._bucket, Key=path)
            last_modified: datetime = head["LastModified"]
            return File(
                key=path,
                size=head["ContentLength"],
                content_type=head.get("ContentType", "application/octet-stream"),
                last_modified=last_modified,
                storage=self,
            )
        except ClientError as exc:
            if exc.response["Error"]["Code"] not in ("404", "NoSuchKey"):
                raise FSStorageError(str(exc)) from exc

        # Check if it is a folder (prefix with children)
        folder_prefix = path.rstrip("/") + "/"
        resp = self._s3.list_objects_v2(
            Bucket=self._bucket, Prefix=folder_prefix, MaxKeys=1
        )
        if resp.get("KeyCount", 0) > 0 or resp.get("Contents"):
            return Directory(path=folder_prefix, storage=self)

        raise FSNodeNotFoundError(path)

    def list_direct_children(self, prefix: str) -> list[FSNode]:
        """List immediate children of a folder prefix (non-recursive)."""
        from filesystem.domain.entities import Directory, File  # noqa: PLC0415

        prefix = prefix.rstrip("/") + "/"
        resp = self._s3.list_objects_v2(
            Bucket=self._bucket, Prefix=prefix, Delimiter="/"
        )

        nodes: list[FSNode] = []

        # Sub-folders (common prefixes)
        for cp in resp.get("CommonPrefixes") or []:
            sub_prefix = cp["Prefix"]
            nodes.append(Directory(path=sub_prefix, storage=self))

        # Files
        for obj in resp.get("Contents") or []:
            key: str = obj["Key"]
            if key == prefix:
                # Skip the folder marker itself
                continue
            nodes.append(
                File(
                    key=key,
                    size=obj["Size"],
                    content_type="application/octet-stream",
                    last_modified=obj["LastModified"],
                    storage=self,
                )
            )

        return nodes

    def put_folder(self, path: str) -> None:
        """Create a folder marker in S3."""
        key = path.rstrip("/") + "/"
        self._s3.put_object(Bucket=self._bucket, Key=key, Body=b"")

    def put_file(self, path: str, content: bytes, content_type: str) -> None:
        """Upload a file to S3."""
        self._s3.put_object(
            Bucket=self._bucket,
            Key=path,
            Body=content,
            ContentType=content_type,
        )

    def delete_object(self, key: str) -> None:
        """Delete a single S3 object (ignore if not found)."""
        try:
            self._s3.delete_object(Bucket=self._bucket, Key=key)
        except ClientError as exc:
            code = exc.response["Error"]["Code"]
            if code not in ("404", "NoSuchKey"):
                raise FSStorageError(str(exc)) from exc
