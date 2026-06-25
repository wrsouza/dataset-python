"""Unit tests for the CloudEvent domain entity."""

from __future__ import annotations

import pytest

from cloud_event_notifier.domain.entities import CloudEvent


def test_cloud_event_rejects_empty_event_type() -> None:
    with pytest.raises(ValueError, match="event_type"):
        CloudEvent(event_type="   ", payload={})


def test_cloud_event_generates_unique_id_by_default() -> None:
    first = CloudEvent(event_type="order.created", payload={})
    second = CloudEvent(event_type="order.created", payload={})

    assert first.event_id != second.event_id
