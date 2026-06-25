"""Domain entities for the Cache Decorator API.

Defines the value objects exchanged between the Component (DataService),
the decorators, and the application layer.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DataQuery:
    """A request for a product quote, identified by its product key.

    Frozen so it can be safely used as a cache key / dict key across
    decorators without risk of accidental mutation.
    """

    product_id: str

    def cache_key(self) -> str:
        """Return the deterministic cache key for this query."""
        return f"quote:{self.product_id.lower()}"


@dataclass(frozen=True)
class DataResult:
    """The outcome of a data query: a product quote at a point in time."""

    product_id: str
    price: float
    currency: str
    fetched_at: str
