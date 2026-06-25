"""S3 (LocalStack) image storage implementation — infrastructure layer."""

from __future__ import annotations

import boto3
from botocore.exceptions import ClientError

from thumbnails.domain.exceptions import ImageNotFoundError


class S3ImageStorage:
    """Concrete storage backed by S3 (LocalStack in dev, real S3 in prod).

    Injected into use cases via ImageStorageProtocol — never imported directly
    by application layer code (DIP compliance).
    """

    def __init__(self, bucket: str, endpoint_url: str | None = None) -> None:
        self._bucket = bucket
        self._client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id="test",
            aws_secret_access_key="test",
            region_name="us-east-1",
        )
        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        """Create bucket if it does not exist."""
        try:
            self._client.head_bucket(Bucket=self._bucket)
        except ClientError:
            self._client.create_bucket(Bucket=self._bucket)

    def upload(self, key: str, data: bytes, content_type: str) -> str:
        """Upload binary data to S3 and return the object key."""
        self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        return key

    def download(self, key: str) -> bytes:
        """Download object from S3; raises ImageNotFoundError if missing."""
        try:
            response = self._client.get_object(Bucket=self._bucket, Key=key)
            return response["Body"].read()
        except ClientError as exc:
            error_code = exc.response["Error"]["Code"]
            if error_code in ("NoSuchKey", "404"):
                raise ImageNotFoundError(key) from exc
            raise

    def exists(self, key: str) -> bool:
        """Check if an object exists in S3."""
        try:
            self._client.head_object(Bucket=self._bucket, Key=key)
            return True
        except ClientError:
            return False

    def get_url(self, key: str) -> str:
        """Return a presigned URL for the object."""
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket, "Key": key},
            ExpiresIn=3600,
        )
