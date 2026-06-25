"""Integration tests for the Flask S3 bucket iterator API."""

from __future__ import annotations

import pytest
from flask.testing import FlaskClient

from s3_iterator.app import create_app
from tests.unit.test_object_iterator import FakeS3ObjectSource


@pytest.fixture
def client() -> FlaskClient:
    app = create_app(source=FakeS3ObjectSource(total=10))
    app.config.update(TESTING=True)
    return app.test_client()


def test_health_check(client: FlaskClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_list_objects_returns_first_page(client: FlaskClient) -> None:
    response = client.get("/objects", query_string={"limit": 4})

    body = response.get_json()
    assert [item["key"] for item in body["items"]] == [
        "file-000.txt",
        "file-001.txt",
        "file-002.txt",
        "file-003.txt",
    ]
    assert body["next_token"] == "4"


def test_list_objects_follows_continuation_token(client: FlaskClient) -> None:
    first = client.get("/objects", query_string={"limit": 4}).get_json()

    second = client.get(
        "/objects", query_string={"limit": 4, "continuation_token": first["next_token"]}
    ).get_json()

    assert second["items"][0]["key"] == "file-004.txt"


def test_summary_aggregates_entire_bucket(client: FlaskClient) -> None:
    response = client.get("/objects/summary")

    body = response.get_json()
    assert body["object_count"] == 10
    assert body["total_size_bytes"] == sum(range(10))
