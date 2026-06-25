"""Testes unitários do ConcreteComponent (ProcessOrderUseCase)."""

from __future__ import annotations

import pytest

from observability.application.use_cases import ProcessOrderUseCase
from observability.domain.entities import OrderRequest, OrderStatus
from observability.domain.exceptions import InvalidOrderError


def test_process_returns_processed_result_for_valid_order() -> None:
    use_case = ProcessOrderUseCase()
    request = OrderRequest(
        customer_id="c1", item_sku="sku1", quantity=2, unit_price=5.0
    )

    result = use_case.process(request)

    assert result.status == OrderStatus.PROCESSED
    assert result.total_amount == 10.0


@pytest.mark.parametrize(
    ("quantity", "unit_price"),
    [(0, 5.0), (-1, 5.0), (1001, 5.0), (1, 0.0), (1, -2.0)],
)
def test_process_raises_for_invalid_order(quantity: int, unit_price: float) -> None:
    use_case = ProcessOrderUseCase()
    request = OrderRequest(
        customer_id="c1", item_sku="sku1", quantity=quantity, unit_price=unit_price
    )

    with pytest.raises(InvalidOrderError):
        use_case.process(request)
