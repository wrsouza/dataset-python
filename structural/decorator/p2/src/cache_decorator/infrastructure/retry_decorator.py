"""ConcreteDecorator: RetryDecorator — retries on failure with backoff.

Pattern role: wraps any DataService to add resilience without coupling
the resilience policy to the data-fetching logic (SRP, OCP).
"""

from __future__ import annotations

import logging
import time

from cache_decorator.domain.entities import DataQuery, DataResult
from cache_decorator.domain.interfaces import DataService, DataServiceDecorator

logger = logging.getLogger(__name__)

DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_BACKOFF_SECONDS = 0.1


class RetryDecorator(DataServiceDecorator):
    """Retries `get_data` up to `max_attempts` times on any exception.

    Uses a simple linear backoff: `backoff_seconds * attempt_number`
    between attempts. The last failure is re-raised unchanged so callers
    keep seeing the same exception type as an undecorated service (LSP).
    """

    def __init__(
        self,
        wrapped: DataService,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        backoff_seconds: float = DEFAULT_BACKOFF_SECONDS,
    ) -> None:
        super().__init__(wrapped)
        self._max_attempts = max_attempts
        self._backoff_seconds = backoff_seconds

    def get_data(self, query: DataQuery) -> DataResult:
        """Call the wrapped service, retrying on exception with backoff."""
        last_error: Exception | None = None
        for attempt in range(1, self._max_attempts + 1):
            try:
                return self._wrapped.get_data(query)
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                logger.warning(
                    "get_data attempt %d/%d failed for product_id=%s: %s",
                    attempt,
                    self._max_attempts,
                    query.product_id,
                    exc,
                )
                if attempt < self._max_attempts:
                    time.sleep(self._backoff_seconds * attempt)
        if last_error is None:  # pragma: no cover — defensive, loop always sets it
            raise RuntimeError("RetryDecorator exhausted attempts without an error")
        raise last_error
