"""Domain exceptions for the Shopping Cart Visitors system."""

from __future__ import annotations


class InvalidOperationError(Exception):
    """Raised when an operation name is not registered."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Unknown cart operation '{name}'")
        self.name = name


class InvalidItemTypeError(Exception):
    """Raised when a cart item's `type` field is not recognised."""

    def __init__(self, item_type: str) -> None:
        super().__init__(f"Unknown cart item type '{item_type}'")
        self.item_type = item_type
