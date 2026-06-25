"""Testes unitários do Decorator base."""

from __future__ import annotations

from observability.domain.entities import OrderRequest, OrderResult, OrderStatus
from observability.domain.interfaces import OrderProcessor
from observability.infrastructure.observability_decorator import (
    ObservabilityDecorator,
)


class _StubProcessor(OrderProcessor):
    def process(self, request: OrderRequest) -> OrderResult:
        return OrderResult.new_processed(total_amount=request.total_amount())


def test_base_decorator_delegates_to_wrapped_component() -> None:
    decorator = ObservabilityDecorator(_StubProcessor())
    request = OrderRequest(
        customer_id="c1", item_sku="sku1", quantity=1, unit_price=2.0
    )

    result = decorator.process(request)

    assert result.status == OrderStatus.PROCESSED
    assert result.total_amount == 2.0
