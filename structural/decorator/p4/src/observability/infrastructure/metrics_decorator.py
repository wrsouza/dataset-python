"""ConcreteDecorator: instrumenta a operação com métricas de duração."""

from __future__ import annotations

import time

from observability.domain.entities import OrderRequest, OrderResult
from observability.domain.interfaces import MetricsPublisher, OrderProcessor
from observability.infrastructure.observability_decorator import (
    ObservabilityDecorator,
)

MILLISECONDS_PER_SECOND = 1000


class MetricsDecorator(ObservabilityDecorator):
    """Publica métricas de duração e contagem de chamadas via MetricsPublisher."""

    def __init__(self, wrapped: OrderProcessor, publisher: MetricsPublisher) -> None:
        super().__init__(wrapped)
        self._publisher = publisher

    def process(self, request: OrderRequest) -> OrderResult:
        """Mede a duração da chamada delegada e publica como métrica."""
        started_at = time.perf_counter()
        result = self._wrapped.process(request)
        duration_ms = (time.perf_counter() - started_at) * MILLISECONDS_PER_SECOND

        dimensions = {"Operation": "process_order"}
        self._publisher.put_metric(
            "ProcessOrderDuration", duration_ms, "Milliseconds", dimensions
        )
        self._publisher.put_metric("ProcessOrderCount", 1.0, "Count", dimensions)
        return result
