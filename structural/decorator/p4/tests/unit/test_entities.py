"""Testes unitários das entidades de domínio."""

from __future__ import annotations

from observability.domain.entities import OrderRequest, OrderResult, OrderStatus


def test_order_request_total_amount_multiplies_quantity_by_price() -> None:
    request = OrderRequest(
        customer_id="c1", item_sku="sku1", quantity=3, unit_price=10.5
    )

    assert request.total_amount() == 31.5


def test_order_result_new_processed_sets_processed_status() -> None:
    result = OrderResult.new_processed(total_amount=99.9)

    assert result.status == OrderStatus.PROCESSED
    assert result.total_amount == 99.9
    assert result.order_id
