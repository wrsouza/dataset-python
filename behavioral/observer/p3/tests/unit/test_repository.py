"""Unit tests for DjangoOrderRepository against a real (in-memory SQLite) ORM."""

from __future__ import annotations

import pytest

from order_signals.infrastructure.repository import DjangoOrderRepository

pytestmark = pytest.mark.django_db


def test_save_and_find_by_id_round_trips_order() -> None:
    repository = DjangoOrderRepository()

    repository.save("o1", 10.0, status="created")
    order = repository.find_by_id("o1")

    assert order is not None
    assert order.total == 10.0
    assert order.status == "created"


def test_find_by_id_returns_none_when_missing() -> None:
    repository = DjangoOrderRepository()

    assert repository.find_by_id("unknown") is None


def test_save_updates_existing_order() -> None:
    repository = DjangoOrderRepository()
    repository.save("o1", 10.0, status="created")

    repository.save("o1", 10.0, status="shipped")

    order = repository.find_by_id("o1")
    assert order is not None
    assert order.status == "shipped"
