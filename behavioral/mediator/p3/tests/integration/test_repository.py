"""Integration tests for DjangoNotificationRepository against a real ORM."""

from __future__ import annotations

import pytest

from realtime_notifications.domain.entities import Notification
from realtime_notifications.infrastructure.repository import (
    DjangoNotificationRepository,
)

pytestmark = pytest.mark.django_db


def test_save_and_list_for_group_round_trips() -> None:
    repository = DjangoNotificationRepository()
    repository.save(Notification(group="room-1", message={"text": "hi"}))

    results = repository.list_for_group("room-1")

    assert len(results) == 1
    assert results[0].message == {"text": "hi"}


def test_list_for_group_filters_other_groups() -> None:
    repository = DjangoNotificationRepository()
    repository.save(Notification(group="room-1", message={"text": "a"}))
    repository.save(Notification(group="room-2", message={"text": "b"}))

    results = repository.list_for_group("room-1")

    assert len(results) == 1


def test_list_for_group_returns_empty_for_unknown_group() -> None:
    repository = DjangoNotificationRepository()

    assert repository.list_for_group("ghost") == []
