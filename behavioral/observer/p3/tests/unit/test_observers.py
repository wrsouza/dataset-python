"""Unit tests for AuditLogObserver and NotificationObserver, against a real
(in-memory SQLite) ORM."""

from __future__ import annotations

import pytest

from order_signals.domain.entities import OrderEvent
from order_signals.infrastructure.observers import (
    AuditLogObserver,
    NotificationObserver,
)
from order_signals.infrastructure.repository import (
    DjangoAuditLogRepository,
    DjangoNotificationLogRepository,
)

pytestmark = pytest.mark.django_db


def test_audit_log_observer_writes_one_entry_per_event() -> None:
    observer = AuditLogObserver()

    observer.on_order_event(OrderEvent(order_id="o1", status="created", total=10.0))

    entries = DjangoAuditLogRepository().list_for_order("o1")
    assert len(entries) == 1
    assert "created" in entries[0].message


def test_notification_observer_writes_one_entry_per_event() -> None:
    observer = NotificationObserver(channel="sms")

    observer.on_order_event(OrderEvent(order_id="o1", status="shipped", total=10.0))

    entries = DjangoNotificationLogRepository().list_for_order("o1")
    assert len(entries) == 1
    assert entries[0].channel == "sms"
    assert "shipped" in entries[0].message
