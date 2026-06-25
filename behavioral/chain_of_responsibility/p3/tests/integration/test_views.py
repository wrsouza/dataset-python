"""Integration tests for the moderation Django views, end-to-end with moto."""

from __future__ import annotations

import json

import pytest
from django.test import Client
from moto import mock_aws

pytestmark = pytest.mark.django_db


@mock_aws
def test_submit_clean_text_is_approved(client: Client) -> None:
    response = client.post(
        "/submissions/",
        data=json.dumps({"author": "alice", "text": "hello world"}),
        content_type="application/json",
    )

    body = response.json()
    assert response.status_code == 201
    assert body["status"] == "approved"


@mock_aws
def test_submit_banned_word_is_rejected(client: Client) -> None:
    response = client.post(
        "/submissions/",
        data=json.dumps({"author": "bob", "text": "this looks like scam"}),
        content_type="application/json",
    )

    body = response.json()
    assert body["status"] == "rejected"
    assert body["history"][0]["handler_name"] == "TextProfanityHandler"


@mock_aws
def test_get_submission_after_submission(client: Client) -> None:
    submit_response = client.post(
        "/submissions/",
        data=json.dumps({"author": "carol", "text": "all good here"}),
        content_type="application/json",
    )
    submission_id = submit_response.json()["submission_id"]

    get_response = client.get(f"/submissions/{submission_id}/")

    assert get_response.status_code == 200
    assert get_response.json()["submission_id"] == submission_id


@mock_aws
def test_get_unknown_submission_returns_404(client: Client) -> None:
    response = client.get("/submissions/does-not-exist/")

    assert response.status_code == 404
