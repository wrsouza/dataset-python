"""Unit tests for the Shopping Cart Visitors use cases."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator

import pytest

from shopping_cart_visitors.application.use_cases import (
    GetCartReportsUseCase,
    RunCartOperationInput,
    RunCartOperationUseCase,
)
from shopping_cart_visitors.domain.exceptions import (
    InvalidItemTypeError,
    InvalidOperationError,
)
from shopping_cart_visitors.infrastructure.repository import CartReportRepository


@pytest.fixture
def repository() -> Iterator[CartReportRepository]:
    connection = sqlite3.connect(":memory:")
    try:
        yield CartReportRepository(connection, dialect="sqlite")
    finally:
        connection.close()


def test_run_price_operation_persists_report(
    repository: CartReportRepository,
) -> None:
    use_case = RunCartOperationUseCase(repository)

    report = use_case.execute(
        RunCartOperationInput(
            operation="price",
            items=[
                {
                    "type": "physical",
                    "name": "Book",
                    "unit_price": 10.0,
                    "quantity": 1,
                    "weight_kg": 0.5,
                }
            ],
        )
    )

    assert report.data["subtotal"] == 10.0
    assert len(repository.list_for_operation(report.operation)) == 1


def test_run_operation_raises_for_unknown_operation(
    repository: CartReportRepository,
) -> None:
    use_case = RunCartOperationUseCase(repository)

    with pytest.raises(InvalidOperationError):
        use_case.execute(RunCartOperationInput(operation="unknown", items=[]))


def test_run_operation_raises_for_unknown_item_type(
    repository: CartReportRepository,
) -> None:
    use_case = RunCartOperationUseCase(repository)

    with pytest.raises(InvalidItemTypeError):
        use_case.execute(
            RunCartOperationInput(operation="price", items=[{"type": "unknown"}])
        )


def test_get_cart_reports_use_case_returns_history(
    repository: CartReportRepository,
) -> None:
    RunCartOperationUseCase(repository).execute(
        RunCartOperationInput(
            operation="shipping",
            items=[
                {
                    "type": "physical",
                    "name": "Book",
                    "unit_price": 10.0,
                    "quantity": 1,
                    "weight_kg": 1.0,
                }
            ],
        )
    )

    history = GetCartReportsUseCase(repository).execute("shipping")

    assert len(history) == 1


def test_get_cart_reports_use_case_raises_for_unknown_operation(
    repository: CartReportRepository,
) -> None:
    with pytest.raises(InvalidOperationError):
        GetCartReportsUseCase(repository).execute("unknown")
