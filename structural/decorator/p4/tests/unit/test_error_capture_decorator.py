"""Testes unitários do ErrorCaptureDecorator com fake ErrorReporter."""

from __future__ import annotations

import pytest

from observability.application.use_cases import ProcessOrderUseCase
from observability.domain.entities import OrderRequest
from observability.domain.exceptions import InvalidOrderError
from observability.infrastructure.error_capture_decorator import (
    ErrorCaptureDecorator,
)


class _FakeErrorReporter:
    def __init__(self) -> None:
        self.reports: list[tuple[str, BaseException, dict[str, str]]] = []

    def report_error(
        self, operation: str, error: BaseException, attributes: dict[str, str]
    ) -> None:
        self.reports.append((operation, error, attributes))


def test_error_capture_decorator_reports_and_reraises_invalid_order() -> None:
    reporter = _FakeErrorReporter()
    decorator = ErrorCaptureDecorator(ProcessOrderUseCase(), reporter)
    request = OrderRequest(
        customer_id="c1", item_sku="sku1", quantity=0, unit_price=5.0
    )

    with pytest.raises(InvalidOrderError):
        decorator.process(request)

    assert len(reporter.reports) == 1
    operation, error, attributes = reporter.reports[0]
    assert operation == "process_order"
    assert isinstance(error, InvalidOrderError)
    assert attributes["customer_id"] == "c1"


def test_error_capture_decorator_passes_through_successful_result() -> None:
    reporter = _FakeErrorReporter()
    decorator = ErrorCaptureDecorator(ProcessOrderUseCase(), reporter)
    request = OrderRequest(
        customer_id="c1", item_sku="sku1", quantity=1, unit_price=5.0
    )

    result = decorator.process(request)

    assert result.total_amount == 5.0
    assert not reporter.reports
