"""Unit tests for Product and ProductSnapshot domain entities."""

from __future__ import annotations

import pytest

from audit_trail_records.domain.entities import Product, ProductSnapshot


def test_snapshot_rejects_invalid_version() -> None:
    with pytest.raises(ValueError, match="version"):
        ProductSnapshot(name="x", price=1.0, stock=1, version=0, changed_by="ana")


def test_snapshot_rejects_empty_changed_by() -> None:
    with pytest.raises(ValueError, match="changed_by"):
        ProductSnapshot(name="x", price=1.0, stock=1, version=1, changed_by="   ")


def test_create_snapshot_captures_current_state() -> None:
    product = Product(product_id="p1", name="Widget", price=9.99, stock=10)
    product.set_changed_by("ana")

    snapshot = product.create_snapshot()

    assert snapshot.name == "Widget"
    assert snapshot.price == 9.99
    assert snapshot.stock == 10
    assert snapshot.version == 1
    assert snapshot.changed_by == "ana"


def test_restore_replaces_fields_and_version() -> None:
    product = Product(product_id="p1", name="Widget", price=9.99, stock=10)
    snapshot = ProductSnapshot(
        name="Gadget", price=19.99, stock=5, version=3, changed_by="bob"
    )

    product.restore(snapshot)

    assert product.name == "Gadget"
    assert product.price == 19.99
    assert product.stock == 5
    assert product.current_version == 3


def test_apply_edit_increments_version() -> None:
    product = Product(product_id="p1", name="Widget", price=9.99, stock=10)

    product.apply_edit("Widget 2", 12.5, 8)

    assert product.name == "Widget 2"
    assert product.price == 12.5
    assert product.stock == 8
    assert product.current_version == 2
