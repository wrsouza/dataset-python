"""Teste de integração: cadeia completa de decoradores via factory + moto."""

from __future__ import annotations

from observability.domain.entities import OrderRequest, OrderStatus
from observability.domain.exceptions import InvalidOrderError
from observability.infrastructure.factory import build_instrumented_order_processor
from observability.infrastructure.settings import Settings


def test_instrumented_processor_processes_order_end_to_end(moto_aws: None) -> None:
    settings = Settings.from_env()
    processor = build_instrumented_order_processor(settings)
    request = OrderRequest(
        customer_id="c1", item_sku="sku1", quantity=3, unit_price=7.5
    )

    result = processor.process(request)

    assert result.status == OrderStatus.PROCESSED
    assert result.total_amount == 22.5


def test_instrumented_processor_reports_and_reraises_invalid_order(
    moto_aws: None,
) -> None:
    settings = Settings.from_env()
    processor = build_instrumented_order_processor(settings)
    request = OrderRequest(
        customer_id="c1", item_sku="sku1", quantity=-1, unit_price=7.5
    )

    try:
        processor.process(request)
        raise AssertionError("expected InvalidOrderError")
    except InvalidOrderError:
        pass
