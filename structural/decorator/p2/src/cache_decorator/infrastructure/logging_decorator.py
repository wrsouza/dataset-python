"""ConcreteDecorator: LoggingDecorator — logs calls and execution time.

Pattern role: wraps any DataService to add observability without
touching the wrapped service's logic (SRP, OCP).
"""

from __future__ import annotations

import logging
import time

from cache_decorator.domain.entities import DataQuery, DataResult
from cache_decorator.domain.interfaces import DataServiceDecorator

logger = logging.getLogger(__name__)


class LoggingDecorator(DataServiceDecorator):
    """Logs each `get_data` call together with its duration."""

    def get_data(self, query: DataQuery) -> DataResult:
        """Delegate to the wrapped service, logging start, end, and duration."""
        started_at = time.perf_counter()
        logger.info("get_data started for product_id=%s", query.product_id)
        try:
            result = self._wrapped.get_data(query)
        except Exception:
            elapsed_ms = (time.perf_counter() - started_at) * 1000
            logger.exception(
                "get_data failed for product_id=%s after %.2fms",
                query.product_id,
                elapsed_ms,
            )
            raise
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        logger.info(
            "get_data finished for product_id=%s in %.2fms",
            query.product_id,
            elapsed_ms,
        )
        return result
