"""ConcreteDecorator: instrumenta a operação com spans de tracing."""

from __future__ import annotations

import time

from observability.domain.entities import OrderRequest, OrderResult
from observability.domain.interfaces import OrderProcessor, TraceExporter
from observability.infrastructure.observability_decorator import (
    ObservabilityDecorator,
)

MILLISECONDS_PER_SECOND = 1000


class TracingDecorator(ObservabilityDecorator):
    """Exporta um span representando a execução da operação decorada."""

    def __init__(self, wrapped: OrderProcessor, exporter: TraceExporter) -> None:
        super().__init__(wrapped)
        self._exporter = exporter

    def process(self, request: OrderRequest) -> OrderResult:
        """Cria e exporta um span cobrindo a chamada delegada."""
        started_at = time.perf_counter()
        result = self._wrapped.process(request)
        duration_ms = (time.perf_counter() - started_at) * MILLISECONDS_PER_SECOND

        self._exporter.export_span(
            operation="process_order",
            duration_ms=duration_ms,
            attributes={
                "customer_id": request.customer_id,
                "order_id": result.order_id,
                "status": result.status.value,
            },
        )
        return result
