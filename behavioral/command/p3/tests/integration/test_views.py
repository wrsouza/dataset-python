"""Integration tests for the scheduled_executor Django views.

CELERY_TASK_ALWAYS_EAGER (set in config.settings_test) makes the worker
task run synchronously in-process, so these tests never need a real
Redis broker.
"""

from __future__ import annotations

import json

import pytest
from django.test import Client

pytestmark = pytest.mark.django_db


def test_trigger_backup_command_returns_success(client: Client) -> None:
    response = client.post(
        "/commands/trigger/",
        data=json.dumps({"command_name": "backup", "payload": {"target": "orders-db"}}),
        content_type="application/json",
    )

    body = response.json()
    assert response.status_code == 201
    assert body["status"] == "success"
    assert "orders-db" in body["result_message"]


def test_trigger_unknown_command_returns_400(client: Client) -> None:
    response = client.post(
        "/commands/trigger/",
        data=json.dumps({"command_name": "nope", "payload": {}}),
        content_type="application/json",
    )

    assert response.status_code == 400


def test_get_execution_status_after_trigger(client: Client) -> None:
    trigger_response = client.post(
        "/commands/trigger/",
        data=json.dumps({"command_name": "cleanup", "payload": {"older_than_days": 5}}),
        content_type="application/json",
    )
    job_id = trigger_response.json()["job_id"]

    status_response = client.get(f"/commands/{job_id}/")

    assert status_response.status_code == 200
    assert status_response.json()["job_id"] == job_id


def test_get_execution_status_for_unknown_job_returns_404(client: Client) -> None:
    response = client.get("/commands/does-not-exist/")

    assert response.status_code == 404
