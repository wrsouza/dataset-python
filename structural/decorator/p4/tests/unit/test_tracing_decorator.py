"""Testes unitários do TracingDecorator com fake TraceExporter."""

from __future__ import annotations

from observability.application.use_cases import ProcessOrderUseCase
from observability.domain.entities import OrderRequest
from observability.infrastructure.tracing_decorator import TracingDecorator


class _FakeTraceExporter:
    def __init__(self) -> None:
        self.spans: list[tuple[str, float, dict[str, str]]] = []

    def export_span(
        self, operation: str, duration_ms: float, attributes: dict[str, str]
    ) -> None:
        self.spans.append((operation, duration_ms, attributes))


def test_tracing_decorator_exports_span_with_order_attributes() -> None:
    exporter = _FakeTraceExporter()
    decorator = TracingDecorator(ProcessOrderUseCase(), exporter)
    request = OrderRequest(
        customer_id="c1", item_sku="sku1", quantity=1, unit_price=5.0
    )

    result = decorator.process(request)

    assert len(exporter.spans) == 1
    operation, duration_ms, attributes = exporter.spans[0]
    assert operation == "process_order"
    assert duration_ms >= 0
    assert attributes["customer_id"] == "c1"
    assert attributes["order_id"] == result.order_id
