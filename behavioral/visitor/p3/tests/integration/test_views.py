"""Integration tests for the content_export_visitor Django views, using
moto to fake AWS S3."""

from __future__ import annotations

import json
from collections.abc import Iterator

import boto3
import pytest
from django.test import Client
from moto import mock_aws

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def s3_bucket() -> Iterator[None]:
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="content-exports")
        yield


def test_export_content_returns_201(client: Client) -> None:
    response = client.post(
        "/exports/json/",
        data=json.dumps(
            {"nodes": [{"type": "article", "title": "Hello", "body": "World"}]}
        ),
        content_type="application/json",
    )

    body = response.json()
    assert response.status_code == 201
    assert body["format"] == "json"


def test_export_content_unknown_format_returns_400(client: Client) -> None:
    response = client.post(
        "/exports/pdf/",
        data=json.dumps({"nodes": []}),
        content_type="application/json",
    )

    assert response.status_code == 400


def test_get_export_job_after_export(client: Client) -> None:
    export_response = client.post(
        "/exports/markdown/",
        data=json.dumps({"nodes": [{"type": "image", "url": "http://x"}]}),
        content_type="application/json",
    )
    job_id = export_response.json()["job_id"]

    response = client.get(f"/exports/jobs/{job_id}/")

    assert response.status_code == 200
    assert response.json()["job_id"] == job_id


def test_get_export_job_unknown_returns_404(client: Client) -> None:
    response = client.get("/exports/jobs/does-not-exist/")

    assert response.status_code == 404
