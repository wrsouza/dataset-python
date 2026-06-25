"""Unit tests for CartReportRepository against a real (in-memory SQLite)
DB-API connection."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator

import pytest

from shopping_cart_visitors.domain.entities import CartReport, OperationType
from shopping_cart_visitors.infrastructure.repository import CartReportRepository


@pytest.fixture
def connection() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()


@pytest.fixture
def repository(connection: sqlite3.Connection) -> CartReportRepository:
    return CartReportRepository(connection, dialect="sqlite")


def test_save_and_list_for_operation_round_trips(
    repository: CartReportRepository,
) -> None:
    report = CartReport(operation=OperationType.PRICE, data={"total": 10.0})
    repository.save(report)

    history = repository.list_for_operation(OperationType.PRICE)

    assert history == [report]


def test_list_for_operation_only_returns_matching_operation(
    repository: CartReportRepository,
) -> None:
    repository.save(CartReport(operation=OperationType.PRICE, data={"total": 10.0}))
    repository.save(CartReport(operation=OperationType.SHIPPING, data={"cost": 5.0}))

    history = repository.list_for_operation(OperationType.PRICE)

    assert len(history) == 1


def test_list_for_operation_empty_when_no_reports(
    repository: CartReportRepository,
) -> None:
    assert repository.list_for_operation(OperationType.INVOICE) == []
