"""Unit tests for the item factory."""

from __future__ import annotations

import pytest

from shopping_cart_visitors.application.item_factory import build_item, build_items
from shopping_cart_visitors.domain.exceptions import InvalidItemTypeError
from shopping_cart_visitors.domain.interfaces import (
    DigitalItem,
    PhysicalItem,
    SubscriptionItem,
)


def test_build_item_physical() -> None:
    item = build_item(
        {
            "type": "physical",
            "name": "Book",
            "unit_price": 10.0,
            "quantity": 1,
            "weight_kg": 0.5,
        }
    )

    assert isinstance(item, PhysicalItem)


def test_build_item_digital() -> None:
    item = build_item(
        {"type": "digital", "name": "E-book", "unit_price": 5.0, "quantity": 1}
    )

    assert isinstance(item, DigitalItem)


def test_build_item_subscription() -> None:
    item = build_item(
        {
            "type": "subscription",
            "name": "Pro",
            "unit_price": 10.0,
            "quantity": 1,
            "billing_period": "monthly",
        }
    )

    assert isinstance(item, SubscriptionItem)


def test_build_item_raises_for_unknown_type() -> None:
    with pytest.raises(InvalidItemTypeError):
        build_item({"type": "unknown"})


def test_build_items_builds_a_list() -> None:
    items = build_items(
        [
            {"type": "digital", "name": "E-book", "unit_price": 5.0, "quantity": 1},
            {"type": "digital", "name": "Song", "unit_price": 1.0, "quantity": 3},
        ]
    )

    assert len(items) == 2
