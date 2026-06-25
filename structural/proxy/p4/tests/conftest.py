"""Shared pytest fixtures: a moto-mocked S3 client, bucket and fake subject."""

from __future__ import annotations

from collections.abc import Iterator

import boto3
import pytest
from moto import mock_aws

from src.remote_files.domain.interfaces import FileResource
from src.remote_files.infrastructure.real_s3_file import RealS3File

TEST_BUCKET = "remote-file-proxy-test-bucket"
TEST_REGION = "us-east-1"
TEST_KEY = "documents/report.txt"
TEST_CONTENT = b"hello from the remote bucket"


@pytest.fixture
def moto_s3() -> Iterator[object]:
    """Yield a boto3 S3 client backed by moto's in-memory AWS mock."""
    with mock_aws():
        client = boto3.client("s3", region_name=TEST_REGION)
        client.create_bucket(Bucket=TEST_BUCKET)
        yield client


@pytest.fixture
def populated_moto_s3(moto_s3: object) -> object:
    """Same as moto_s3, but with one object already uploaded."""
    moto_s3.put_object(Bucket=TEST_BUCKET, Key=TEST_KEY, Body=TEST_CONTENT)  # type: ignore[attr-defined]
    return moto_s3


@pytest.fixture
def real_s3_file(populated_moto_s3: object) -> RealS3File:
    """Build a RealS3File wired to the moto-mocked client, pointing at TEST_KEY."""
    return RealS3File(bucket=TEST_BUCKET, key=TEST_KEY, s3_client=populated_moto_s3)


class FakeFileResource:
    """In-memory FileResource test double with call counters.

    Used to prove the Proxy delegates to the RealSubject only on cache
    misses, without depending on moto or real network mocking.
    """

    def __init__(self, key: str, content: bytes, exists: bool = True) -> None:
        self._key = key
        self._content = content
        self._exists = exists
        self.read_calls = 0
        self.exists_calls = 0
        self.size_calls = 0

    @property
    def key(self) -> str:
        return self._key

    @property
    def size(self) -> int:
        self.size_calls += 1
        return len(self._content)

    def exists(self) -> bool:
        self.exists_calls += 1
        return self._exists

    def read(self) -> bytes:
        self.read_calls += 1
        return self._content


@pytest.fixture
def fake_resource() -> FakeFileResource:
    """A FakeFileResource double, independent of FileResource's structural type."""
    return FakeFileResource(key=TEST_KEY, content=TEST_CONTENT)


def _assert_is_file_resource(resource: FileResource) -> None:
    """Helper used by tests to assert structural conformance to the Protocol."""
    assert isinstance(resource, FileResource)
