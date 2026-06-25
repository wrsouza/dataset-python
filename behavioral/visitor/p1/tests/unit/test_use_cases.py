"""Unit tests for AnalyzeQueryUseCase."""

from __future__ import annotations

import pytest

from query_ast.application.use_cases import AnalyzeQueryUseCase, UnknownOperationError
from query_ast.domain.entities import OperationType
from query_ast.infrastructure.visitors import (
    QueryExplainerVisitor,
    QueryValidatorVisitor,
    SQLGeneratorVisitor,
)

FACTORY = {
    OperationType.EXPLAIN: QueryExplainerVisitor,
    OperationType.VALIDATE: QueryValidatorVisitor,
    OperationType.GENERATE_SQL: SQLGeneratorVisitor,
}


def test_execute_generate_sql_builds_expected_statement() -> None:
    use_case = AnalyzeQueryUseCase(visitor_factory=FACTORY)
    report = use_case.execute(
        operation=OperationType.GENERATE_SQL,
        select={"table": "users", "columns": ["id", "name"]},
        where="active = true",
    )
    assert report.data["sql"] == "SELECT id, name FROM users\nWHERE active = true"
    assert report.is_valid is True


def test_execute_validate_reports_errors_for_bad_query() -> None:
    use_case = AnalyzeQueryUseCase(visitor_factory=FACTORY)
    report = use_case.execute(
        operation=OperationType.VALIDATE,
        select={"table": "users", "columns": []},
        limit={"limit": -5},
    )
    assert report.is_valid is False
    assert any("LIMIT must be positive" in err for err in report.errors)


def test_execute_with_joins_and_group_by_and_order_by() -> None:
    use_case = AnalyzeQueryUseCase(visitor_factory=FACTORY)
    report = use_case.execute(
        operation=OperationType.GENERATE_SQL,
        select={"table": "users u", "columns": ["u.id"]},
        joins=[
            {"join_type": "INNER", "table": "orders o", "on_condition": "u.id = o.uid"}
        ],
        group_by=["u.id"],
        order_by=[("u.id", "ASC")],
        limit={"limit": 5, "offset": 0},
    )
    sql = report.data["sql"]
    assert "INNER JOIN orders o ON u.id = o.uid" in sql
    assert "GROUP BY u.id" in sql
    assert "ORDER BY u.id ASC" in sql
    assert "LIMIT 5" in sql


def test_execute_unknown_operation_raises() -> None:
    use_case = AnalyzeQueryUseCase(visitor_factory={})
    with pytest.raises(UnknownOperationError):
        use_case.execute(operation=OperationType.EXPLAIN, select={"table": "users"})
