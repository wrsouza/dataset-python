"""Unit tests for BotoS3ObjectSource using moto."""

from __future__ import annotations

from datetime import datetime

import boto3
from moto import mock_aws

from s3_iterator.infrastructure.s3_source import BotoS3ObjectSource

BUCKET = "test-bucket"


@mock_aws
def _seed_bucket(count: int) -> object:
    client = boto3.client("s3", region_name="us-east-1")
    client.create_bucket(Bucket=BUCKET)
    for i in range(count):
        client.put_object(Bucket=BUCKET, Key=f"file-{i:03d}.txt", Body=b"x" * i)
    return client


@mock_aws
def test_fetch_page_returns_next_token_when_truncated() -> None:
    client = _seed_bucket(5)
    source = BotoS3ObjectSource(client, BUCKET)

    items, next_token = source.fetch_page(None, limit=2)

    assert len(items) == 2
    assert next_token is not None


@mock_aws
def test_fetch_page_returns_none_token_on_last_page() -> None:
    client = _seed_bucket(3)
    source = BotoS3ObjectSource(client, BUCKET)

    items, next_token = source.fetch_page(None, limit=10)

    assert len(items) == 3
    assert next_token is None


@mock_aws
def test_fetch_page_follows_continuation_token() -> None:
    client = _seed_bucket(5)
    source = BotoS3ObjectSource(client, BUCKET)

    first_items, token = source.fetch_page(None, limit=2)
    second_items, _ = source.fetch_page(token, limit=2)

    first_keys = {obj.key for obj in first_items}
    second_keys = {obj.key for obj in second_items}
    assert first_keys.isdisjoint(second_keys)


@mock_aws
def test_fetch_page_maps_object_size() -> None:
    client = _seed_bucket(0)
    client.put_object(Bucket=BUCKET, Key="single.txt", Body=b"hello")
    source = BotoS3ObjectSource(client, BUCKET)

    items, _ = source.fetch_page(None, limit=10)

    assert items[0].key == "single.txt"
    assert items[0].size == 5
    assert isinstance(items[0].last_modified, datetime)
    assert items[0].last_modified.tzinfo is not None


@mock_aws
def test_fetch_page_returns_empty_for_empty_bucket() -> None:
    client = boto3.client("s3", region_name="us-east-1")
    client.create_bucket(Bucket=BUCKET)
    source = BotoS3ObjectSource(client, BUCKET)

    items, next_token = source.fetch_page(None, limit=10)

    assert items == []
    assert next_token is None
