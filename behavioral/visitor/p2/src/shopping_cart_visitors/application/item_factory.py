"""Builds concrete CartItem instances from plain dict payloads (HTTP JSON)."""

from __future__ import annotations

from typing import Any

from shopping_cart_visitors.domain.exceptions import InvalidItemTypeError
from shopping_cart_visitors.domain.interfaces import (
    CartItem,
    DigitalItem,
    PhysicalItem,
    SubscriptionItem,
)


def build_item(payload: dict[str, Any]) -> CartItem:
    item_type = payload.get("type", "")
    if item_type == "physical":
        return PhysicalItem(
            name=payload["name"],
            unit_price=payload["unit_price"],
            quantity=payload["quantity"],
            weight_kg=payload["weight_kg"],
        )
    if item_type == "digital":
        return DigitalItem(
            name=payload["name"],
            unit_price=payload["unit_price"],
            quantity=payload["quantity"],
        )
    if item_type == "subscription":
        return SubscriptionItem(
            name=payload["name"],
            unit_price=payload["unit_price"],
            quantity=payload["quantity"],
            billing_period=payload["billing_period"],
        )
    raise InvalidItemTypeError(item_type)


def build_items(payloads: list[dict[str, Any]]) -> list[CartItem]:
    return [build_item(payload) for payload in payloads]
