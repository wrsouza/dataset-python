"""boto3-backed implementation of S3ObjectSource using list_objects_v2 paging."""

from __future__ import annotations

from typing import Any, Protocol

from s3_iterator.domain.entities import S3Object
from s3_iterator.domain.interfaces import S3ObjectSource


class S3ClientLike(Protocol):
    """Minimal boto3 S3 client contract this source relies on."""

    def list_objects_v2(self, **kwargs: Any) -> dict[str, Any]: ...


class BotoS3ObjectSource(S3ObjectSource):
    """Lists objects in a single S3 bucket, page by page, via boto3."""

    def __init__(self, client: S3ClientLike, bucket: str) -> None:
        self._client = client
        self._bucket = bucket

    def fetch_page(
        self, continuation_token: str | None, limit: int
    ) -> tuple[list[S3Object], str | None]:
        kwargs: dict[str, Any] = {"Bucket": self._bucket, "MaxKeys": limit}
        if continuation_token is not None:
            kwargs["ContinuationToken"] = continuation_token

        response = self._client.list_objects_v2(**kwargs)
        items = [
            S3Object(
                key=obj["Key"], size=obj["Size"], last_modified=obj["LastModified"]
            )
            for obj in response.get("Contents", [])
        ]
        next_token = (
            response["NextContinuationToken"] if response.get("IsTruncated") else None
        )
        return items, next_token
