"""Shared pytest fixtures: a moto-mocked S3 client and storage adapter."""

from __future__ import annotations

from collections.abc import Iterator

import boto3
import pytest
from moto import mock_aws

from filesystem.infrastructure.s3_client import S3StorageClient

TEST_BUCKET = "vfs-test-bucket"
TEST_REGION = "us-east-1"


@pytest.fixture
def moto_s3() -> Iterator[object]:
    """Yield a boto3 S3 client backed by moto's in-memory AWS mock."""
    with mock_aws():
        client = boto3.client("s3", region_name=TEST_REGION)
        yield client


@pytest.fixture
def storage(moto_s3: object) -> S3StorageClient:
    """Build an S3StorageClient wired to the moto-mocked S3 client."""
    return S3StorageClient(s3_client=moto_s3, bucket=TEST_BUCKET)
