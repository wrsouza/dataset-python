"""Integration tests for the order_signals Django views.

These exercise the real, process-wide `order_event_signal` (wired once
at import time in `django_app/views.py`) end to end: creating/updating
an order through HTTP fans out to both AuditLogObserver and
NotificationObserver via the same Django signal.
"""

from __future__ import annotations

import json

import pytest
from django.test import Client

pytestmark = pytest.mark.django_db


def test_create_order_returns_201_and_notifies_both_observers(client: Client) -> None:
    response = client.post(
        "/orders/",
        data=json.dumps({"order_id": "o1", "total": 42.0}),
        content_type="application/json",
    )

    assert response.status_code == 201
    assert response.json()["status"] == "created"

    audit = client.get("/orders/o1/audit/").json()
    notifications = client.get("/orders/o1/notifications/").json()
    assert len(audit) == 1
    assert len(notifications) == 1


def test_update_order_status_appends_new_log_entries(client: Client) -> None:
    client.post(
        "/orders/",
        data=json.dumps({"order_id": "o1", "total": 42.0}),
        content_type="application/json",
    )

    response = client.put(
        "/orders/o1/status/",
        data=json.dumps({"status": "shipped"}),
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json()["status"] == "shipped"

    audit = client.get("/orders/o1/audit/").json()
    notifications = client.get("/orders/o1/notifications/").json()
    assert len(audit) == 2
    assert len(notifications) == 2
    assert "shipped" in audit[-1]
    assert "shipped" in notifications[-1]


def test_audit_log_empty_for_unknown_order(client: Client) -> None:
    response = client.get("/orders/does-not-exist/audit/")

    assert response.status_code == 200
    assert response.json() == []
