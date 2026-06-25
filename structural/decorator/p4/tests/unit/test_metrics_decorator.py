"""Testes unitários do MetricsDecorator com fake MetricsPublisher."""

from __future__ import annotations

from observability.application.use_cases import ProcessOrderUseCase
from observability.domain.entities import OrderRequest
from observability.infrastructure.metrics_decorator import MetricsDecorator


class _FakeMetricsPublisher:
    def __init__(self) -> None:
        self.calls: list[tuple[str, float, str, dict[str, str]]] = []

    def put_metric(
        self, metric_name: str, value: float, unit: str, dimensions: dict[str, str]
    ) -> None:
        self.calls.append((metric_name, value, unit, dimensions))


def test_metrics_decorator_publishes_duration_and_count() -> None:
    publisher = _FakeMetricsPublisher()
    decorator = MetricsDecorator(ProcessOrderUseCase(), publisher)
    request = OrderRequest(
        customer_id="c1", item_sku="sku1", quantity=1, unit_price=10.0
    )

    result = decorator.process(request)

    assert result.total_amount == 10.0
    metric_names = [call[0] for call in publisher.calls]
    assert "ProcessOrderDuration" in metric_names
    assert "ProcessOrderCount" in metric_names
