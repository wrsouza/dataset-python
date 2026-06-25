"""Integration tests for the workflow_approval_fsm Django views.

CELERY_TASK_ALWAYS_EAGER (set in config.settings_test) makes the
notification task run synchronously in-process, so these tests never
need a real Redis broker.
"""

from __future__ import annotations

import json

import pytest
from django.test import Client

pytestmark = pytest.mark.django_db


def test_create_request_returns_201_in_draft(client: Client) -> None:
    response = client.post(
        "/workflows/",
        data=json.dumps({"request_id": "r1", "title": "Buy laptops"}),
        content_type="application/json",
    )

    body = response.json()
    assert response.status_code == 201
    assert body["state"] == "Draft"


def test_submit_then_approve_workflow(client: Client) -> None:
    client.post(
        "/workflows/",
        data=json.dumps({"request_id": "r1", "title": "Buy laptops"}),
        content_type="application/json",
    )
    client.post("/workflows/r1/submit/")

    response = client.post("/workflows/r1/approve/")

    assert response.status_code == 200
    assert response.json()["state"] == "Approved"


def test_reject_workflow(client: Client) -> None:
    client.post(
        "/workflows/",
        data=json.dumps({"request_id": "r1", "title": "Buy laptops"}),
        content_type="application/json",
    )
    client.post("/workflows/r1/submit/")

    response = client.post("/workflows/r1/reject/")

    assert response.status_code == 200
    assert response.json()["state"] == "Rejected"


def test_request_changes_returns_to_draft(client: Client) -> None:
    client.post(
        "/workflows/",
        data=json.dumps({"request_id": "r1", "title": "Buy laptops"}),
        content_type="application/json",
    )
    client.post("/workflows/r1/submit/")

    response = client.post("/workflows/r1/request-changes/")

    assert response.status_code == 200
    assert response.json()["state"] == "Draft"


def test_get_unknown_request_returns_404(client: Client) -> None:
    response = client.get("/workflows/does-not-exist/")

    assert response.status_code == 404


def test_transition_on_unknown_request_returns_404(client: Client) -> None:
    response = client.post("/workflows/does-not-exist/submit/")

    assert response.status_code == 404


def test_invalid_transition_returns_409(client: Client) -> None:
    client.post(
        "/workflows/",
        data=json.dumps({"request_id": "r1", "title": "Buy laptops"}),
        content_type="application/json",
    )

    response = client.post("/workflows/r1/approve/")

    assert response.status_code == 409
