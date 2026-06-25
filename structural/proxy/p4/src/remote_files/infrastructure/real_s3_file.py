"""RealSubject: a file resource that always talks to S3 directly.

RealS3File performs one S3 network call per method invocation. It never
caches anything -- that responsibility belongs entirely to the Proxy. This
keeps RealS3File simple (SRP) and means new proxy behaviours (caching,
permission checks, throttling, ...) can be added without ever touching this
class (OCP).
"""

from __future__ import annotations

import os

import boto3
from botocore.exceptions import ClientError

from src.remote_files.domain.exceptions import (
    FileNotFoundInRemoteError,
    RemoteStorageError,
)

_NOT_FOUND_CODES = {"404", "NoSuchKey"}


class RealS3File:
    """Direct, uncached access to a single object in an S3 bucket."""

    def __init__(
        self,
        bucket: str,
        key: str,
        s3_client: object | None = None,
    ) -> None:
        self._bucket = bucket
        self._key = key
        self._client = s3_client if s3_client is not None else self._build_client()

    @staticmethod
    def _build_client() -> object:
        return boto3.client(
            "s3",
            endpoint_url=os.environ.get("S3_ENDPOINT_URL") or None,
            region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "test"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", "test"),
        )

    @property
    def key(self) -> str:
        """Return the S3 object key this instance points to."""
        return self._key

    @property
    def size(self) -> int:
        """Fetch the object size from S3 via a HEAD request (no download)."""
        try:
            response = self._client.head_object(Bucket=self._bucket, Key=self._key)  # type: ignore[attr-defined]
        except ClientError as exc:
            self._reraise(exc)
        return int(response["ContentLength"])

    def exists(self) -> bool:
        """Check object existence in S3 via a HEAD request (no download)."""
        try:
            self._client.head_object(Bucket=self._bucket, Key=self._key)  # type: ignore[attr-defined]
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "")
            if code in _NOT_FOUND_CODES or code == "404":
                return False
            self._reraise(exc)
        return True

    def read(self) -> bytes:
        """Download the full object body from S3."""
        try:
            response = self._client.get_object(Bucket=self._bucket, Key=self._key)  # type: ignore[attr-defined]
            return response["Body"].read()  # type: ignore[no-any-return]
        except ClientError as exc:
            self._reraise(exc)
            raise  # pragma: no cover - _reraise always raises

    def _reraise(self, exc: ClientError) -> None:
        code = exc.response.get("Error", {}).get("Code", "")
        if code in _NOT_FOUND_CODES:
            raise FileNotFoundInRemoteError(self._bucket, self._key) from exc
        message = exc.response.get("Error", {}).get("Message", str(exc))
        raise RemoteStorageError(self._bucket, self._key, message) from exc
