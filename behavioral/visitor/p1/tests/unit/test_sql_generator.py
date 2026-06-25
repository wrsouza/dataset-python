"""Unit tests for SQLGeneratorVisitor."""

from __future__ import annotations

from query_ast.application.structure import QueryAST
from query_ast.infrastructure.visitors import SQLGeneratorVisitor


def test_generates_simple_select(simple_select_ast: QueryAST) -> None:
    visitor = SQLGeneratorVisitor()
    result = simple_select_ast.accept_visitor(visitor)
    assert result.data["sql"] == "SELECT id, name FROM users"


def test_generates_select_star_when_no_columns() -> None:
    from query_ast.domain.interfaces import SelectNode

    ast = QueryAST(nodes=[SelectNode(columns=[], table="orders")])
    visitor = SQLGeneratorVisitor()
    result = ast.accept_visitor(visitor)
    assert result.data["sql"] == "SELECT * FROM orders"


def test_generates_full_query_with_all_clauses(full_query_ast: QueryAST) -> None:
    visitor = SQLGeneratorVisitor()
    result = full_query_ast.accept_visitor(visitor)
    sql = result.data["sql"]
    assert "SELECT u.id, u.name, o.total FROM users u" in sql
    assert "LEFT JOIN orders o ON u.id = o.user_id" in sql
    assert "WHERE u.active = true" in sql
    assert "GROUP BY u.id" in sql
    assert "ORDER BY u.name ASC" in sql
    assert "LIMIT 50" in sql


def test_limit_with_offset_appends_offset_clause() -> None:
    from query_ast.domain.interfaces import LimitNode, SelectNode

    ast = QueryAST(
        nodes=[
            SelectNode(columns=["id"], table="users"),
            LimitNode(limit=10, offset=20),
        ]
    )
    visitor = SQLGeneratorVisitor()
    result = ast.accept_visitor(visitor)
    assert "LIMIT 10 OFFSET 20" in result.data["sql"]
