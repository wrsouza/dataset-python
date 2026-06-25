"""Unit tests for QueryOptimizerVisitor."""

from __future__ import annotations

from query_ast.application.structure import QueryAST
from query_ast.domain.interfaces import (
    JoinNode,
    LimitNode,
    SelectNode,
    WhereNode,
)
from query_ast.infrastructure.visitors import QueryOptimizerVisitor


def test_warns_about_select_star() -> None:
    ast = QueryAST(nodes=[SelectNode(columns=[], table="users")])
    visitor = QueryOptimizerVisitor()
    result = ast.accept_visitor(visitor)
    assert any("SELECT *" in hint for hint in result.data["hints"])


def test_suggests_index_for_equality_where() -> None:
    ast = QueryAST(
        nodes=[
            SelectNode(columns=["id"], table="users"),
            WhereNode(condition="users.email = 'a@b.com'"),
        ]
    )
    visitor = QueryOptimizerVisitor()
    result = ast.accept_visitor(visitor)
    assert any("index on 'email'" in hint for hint in result.data["hints"])


def test_warns_full_table_scan_without_where(simple_select_ast: QueryAST) -> None:
    visitor = QueryOptimizerVisitor()
    result = simple_select_ast.accept_visitor(visitor)
    assert any("Full table scan" in hint for hint in result.data["hints"])


def test_warns_many_joins() -> None:
    ast = QueryAST(
        nodes=[
            SelectNode(columns=["id"], table="a"),
            JoinNode(join_type="INNER", table="b", on_condition="a.id = b.a_id"),
            JoinNode(join_type="INNER", table="c", on_condition="a.id = c.a_id"),
            JoinNode(join_type="INNER", table="d", on_condition="a.id = d.a_id"),
            JoinNode(join_type="INNER", table="e", on_condition="a.id = e.a_id"),
        ]
    )
    visitor = QueryOptimizerVisitor()
    result = ast.accept_visitor(visitor)
    assert any("More than 3 JOINs" in hint for hint in result.data["hints"])


def test_warns_large_limit() -> None:
    ast = QueryAST(
        nodes=[SelectNode(columns=["id"], table="logs"), LimitNode(limit=5000)]
    )
    visitor = QueryOptimizerVisitor()
    result = ast.accept_visitor(visitor)
    assert any("cursor-based pagination" in hint for hint in result.data["hints"])
