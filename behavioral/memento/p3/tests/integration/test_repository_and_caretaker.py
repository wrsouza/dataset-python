"""Integration tests for DjangoProductRepository and DjangoAuditTrailCaretaker
against a real (in-memory SQLite) ORM."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from audit_trail_records.domain.entities import NoHistoryError, Product, ProductSnapshot
from audit_trail_records.infrastructure.caretaker import DjangoAuditTrailCaretaker
from audit_trail_records.infrastructure.repository import DjangoProductRepository

pytestmark = pytest.mark.django_db


def _product() -> Product:
    return Product(product_id="p1", name="Widget", price=9.99, stock=10)


def _snapshot(version: int = 1) -> ProductSnapshot:
    return ProductSnapshot(
        name="Widget",
        price=9.99,
        stock=10,
        version=version,
        changed_by="ana",
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def test_save_and_find_by_id_round_trips_product() -> None:
    repository = DjangoProductRepository()

    repository.save(_product())
    fetched = repository.find_by_id("p1")

    assert fetched is not None
    assert fetched.name == "Widget"
    assert fetched.stock == 10


def test_find_by_id_returns_none_when_missing() -> None:
    repository = DjangoProductRepository()

    assert repository.find_by_id("unknown") is None


def test_save_updates_existing_product() -> None:
    repository = DjangoProductRepository()
    repository.save(_product())

    updated = _product()
    updated.name = "Widget v2"
    updated.current_version = 2
    repository.save(updated)

    fetched = repository.find_by_id("p1")
    assert fetched is not None
    assert fetched.name == "Widget v2"
    assert fetched.current_version == 2


def test_caretaker_save_and_history_round_trips_snapshots() -> None:
    caretaker = DjangoAuditTrailCaretaker()

    caretaker.save("p1", _snapshot(version=1))
    caretaker.save("p1", _snapshot(version=2))

    history = caretaker.history("p1")

    assert [snap.version for snap in history] == [1, 2]


def test_caretaker_undo_returns_previous_snapshot() -> None:
    caretaker = DjangoAuditTrailCaretaker()
    caretaker.save("p1", _snapshot(version=1))
    caretaker.save("p1", _snapshot(version=2))

    restored = caretaker.undo("p1")

    assert restored.version == 1


def test_caretaker_undo_raises_with_single_snapshot() -> None:
    caretaker = DjangoAuditTrailCaretaker()
    caretaker.save("p1", _snapshot(version=1))

    with pytest.raises(NoHistoryError):
        caretaker.undo("p1")


def test_caretaker_history_empty_for_unknown_product() -> None:
    caretaker = DjangoAuditTrailCaretaker()

    assert caretaker.history("unknown") == []
