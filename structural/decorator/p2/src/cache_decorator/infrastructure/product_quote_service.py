"""ConcreteComponent: ProductQuoteService — an in-memory product catalog.

Pattern role: this is the real DataService implementation that decorators
(caching, logging, retry) wrap without ever modifying it (OCP).
"""

from __future__ import annotations

import time
from datetime import UTC, datetime

from cache_decorator.domain.entities import DataQuery, DataResult
from cache_decorator.domain.exceptions import ProductNotFoundError
from cache_decorator.domain.interfaces import DataService

# Artificial latency makes the cache's effect observable in logs and tests.
_SIMULATED_LATENCY_SECONDS = 0.05

_CATALOG: dict[str, tuple[float, str]] = {
    "sku-001": (19.90, "USD"),
    "sku-002": (149.00, "USD"),
    "sku-003": (5.49, "EUR"),
    "sku-004": (999.99, "USD"),
}


class ProductQuoteService(DataService):
    """ConcreteComponent: looks up product quotes from an in-memory catalog."""

    def get_data(self, query: DataQuery) -> DataResult:
        """Return the current quote for the requested product.

        Raises:
            ProductNotFoundError: if the product is not in the catalog.
        """
        time.sleep(_SIMULATED_LATENCY_SECONDS)
        entry = _CATALOG.get(query.product_id.lower())
        if entry is None:
            raise ProductNotFoundError(query.product_id)
        price, currency = entry
        return DataResult(
            product_id=query.product_id,
            price=price,
            currency=currency,
            fetched_at=datetime.now(UTC).isoformat(),
        )
