"""Application use cases for the Cache Decorator API.

Use cases depend only on the `DataService` abstraction (DIP) — they have
no idea whether the injected service is decorated with caching, logging,
retry, all three, or none.
"""

from __future__ import annotations

from cache_decorator.domain.entities import DataQuery, DataResult
from cache_decorator.domain.interfaces import DataService


class GetProductQuoteUseCase:
    """Fetches the current quote for a product through the DataService chain."""

    def __init__(self, data_service: DataService) -> None:
        self._data_service = data_service

    def execute(self, product_id: str) -> DataResult:
        """Return the quote for `product_id`, delegating to the data service."""
        query = DataQuery(product_id=product_id)
        return self._data_service.get_data(query)
