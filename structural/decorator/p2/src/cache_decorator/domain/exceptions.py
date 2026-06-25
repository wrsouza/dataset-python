"""Domain-specific exceptions for the Cache Decorator API."""

from __future__ import annotations


class ProductNotFoundError(Exception):
    """Raised when a requested product has no quote available."""

    def __init__(self, product_id: str) -> None:
        self.product_id = product_id
        super().__init__(f"No quote available for product '{product_id}'")


class TransientDataServiceError(Exception):
    """Raised by the concrete service to simulate a recoverable failure.

    Used to exercise RetryDecorator in tests without depending on real
    network flakiness.
    """
