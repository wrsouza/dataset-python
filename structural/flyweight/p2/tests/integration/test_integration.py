"""Integration tests: S3ImageStorage (moto) + full use case flow end-to-end."""

from __future__ import annotations

import io

import boto3
import pytest
from moto import mock_aws
from PIL import Image

from thumbnails.application.use_cases import (
    GenerateThumbnailUseCase,
    GetThumbnailUseCase,
)
from thumbnails.domain.exceptions import ImageNotFoundError
from thumbnails.infrastructure.factory import ThumbnailSpecFactory
from thumbnails.infrastructure.repository import InMemoryThumbnailRepository
from thumbnails.infrastructure.storage import S3ImageStorage


@pytest.fixture
def s3_bucket() -> str:
    return "test-images-bucket"


@pytest.fixture
def s3_storage(s3_bucket: str) -> S3ImageStorage:
    with mock_aws():
        storage = S3ImageStorage(bucket=s3_bucket)
        client = boto3.client("s3", region_name="us-east-1")

        buf = io.BytesIO()
        Image.new("RGB", (500, 500), color=(10, 20, 30)).save(buf, format="JPEG")
        client.put_object(Bucket=s3_bucket, Key="photo.jpg", Body=buf.getvalue())

        yield storage


@mock_aws
def test_s3_storage_round_trip_upload_download() -> None:
    storage = S3ImageStorage(bucket="rt-bucket")
    data = b"fake-image-bytes"

    storage.upload("key.jpg", data, content_type="image/jpeg")

    assert storage.exists("key.jpg") is True
    assert storage.download("key.jpg") == data


@mock_aws
def test_s3_storage_download_missing_key_raises() -> None:
    storage = S3ImageStorage(bucket="empty-bucket")

    with pytest.raises(ImageNotFoundError):
        storage.download("missing.jpg")


@mock_aws
def test_s3_storage_exists_false_for_missing_key() -> None:
    storage = S3ImageStorage(bucket="empty-bucket-2")

    assert storage.exists("nope.jpg") is False


@mock_aws
def test_generate_thumbnail_use_case_full_flow_with_real_s3() -> None:
    """End-to-end: real S3ImageStorage (moto) + factory + repository."""
    bucket = "thumb-flow-bucket"
    storage = S3ImageStorage(bucket=bucket)

    buf = io.BytesIO()
    Image.new("RGB", (800, 800), color=(200, 100, 50)).save(buf, format="JPEG")
    storage.upload("source.jpg", buf.getvalue(), content_type="image/jpeg")

    factory = ThumbnailSpecFactory()
    repo = InMemoryThumbnailRepository()
    generate_uc = GenerateThumbnailUseCase(
        storage=storage, repository=repo, factory=factory
    )

    thumbnail = generate_uc.execute("source.jpg", "thumb_sm")

    assert thumbnail.image_key == "source.jpg"
    assert storage.exists(thumbnail.thumbnail_key) is True

    get_uc = GetThumbnailUseCase(repository=repo, factory=factory)
    fetched = get_uc.execute("source.jpg", "thumb_sm")
    assert fetched is thumbnail
