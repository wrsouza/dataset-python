"""Unit tests for QueryValidatorVisitor."""

from __future__ import annotations

from query_ast.application.structure import QueryAST
from query_ast.domain.interfaces import (
    GroupByNode,
    JoinNode,
    LimitNode,
    OrderByNode,
    SelectNode,
    WhereNode,
)
from query_ast.infrastructure.visitors import QueryValidatorVisitor


def test_valid_query_has_no_errors(full_query_ast: QueryAST) -> None:
    visitor = QueryValidatorVisitor()
    result = full_query_ast.accept_visitor(visitor)
    assert result.is_valid is True


def test_missing_table_is_an_error() -> None:
    ast = QueryAST(nodes=[SelectNode(columns=["id"], table="")])
    visitor = QueryValidatorVisitor()
    result = ast.accept_visitor(visitor)
    assert any("FROM table" in err for err in result.errors)


def test_empty_columns_produces_warning() -> None:
    ast = QueryAST(nodes=[SelectNode(columns=[], table="users")])
    visitor = QueryValidatorVisitor()
    result = ast.accept_visitor(visitor)
    assert any("discouraged" in warn for warn in result.warnings)


def test_empty_where_condition_is_an_error() -> None:
    ast = QueryAST(
        nodes=[SelectNode(columns=["id"], table="users"), WhereNode(condition="   ")]
    )
    visitor = QueryValidatorVisitor()
    result = ast.accept_visitor(visitor)
    assert any("empty condition" in err for err in result.errors)


def test_invalid_join_type_is_an_error() -> None:
    ast = QueryAST(
        nodes=[
            SelectNode(columns=["id"], table="users"),
            JoinNode(
                join_type="OUTER", table="orders", on_condition="users.id = orders.uid"
            ),
        ]
    )
    visitor = QueryValidatorVisitor()
    result = ast.accept_visitor(visitor)
    assert any("Invalid JOIN type" in err for err in result.errors)


def test_join_without_on_condition_is_an_error() -> None:
    ast = QueryAST(
        nodes=[
            SelectNode(columns=["id"], table="users"),
            JoinNode(join_type="INNER", table="orders", on_condition=""),
        ]
    )
    visitor = QueryValidatorVisitor()
    result = ast.accept_visitor(visitor)
    assert any("no ON condition" in err for err in result.errors)


def test_invalid_order_by_direction_is_an_error() -> None:
    ast = QueryAST(
        nodes=[
            SelectNode(columns=["id"], table="users"),
            OrderByNode(columns=[("id", "SIDEWAYS")]),
        ]
    )
    visitor = QueryValidatorVisitor()
    result = ast.accept_visitor(visitor)
    assert any("invalid direction" in err for err in result.errors)


def test_empty_group_by_is_an_error() -> None:
    ast = QueryAST(
        nodes=[SelectNode(columns=["id"], table="users"), GroupByNode(columns=[])]
    )
    visitor = QueryValidatorVisitor()
    result = ast.accept_visitor(visitor)
    assert any("no columns" in err for err in result.errors)


def test_non_positive_limit_is_an_error() -> None:
    ast = QueryAST(
        nodes=[SelectNode(columns=["id"], table="users"), LimitNode(limit=0)]
    )
    visitor = QueryValidatorVisitor()
    result = ast.accept_visitor(visitor)
    assert any("LIMIT must be positive" in err for err in result.errors)


def test_negative_offset_is_an_error() -> None:
    ast = QueryAST(
        nodes=[
            SelectNode(columns=["id"], table="users"),
            LimitNode(limit=10, offset=-1),
        ]
    )
    visitor = QueryValidatorVisitor()
    result = ast.accept_visitor(visitor)
    assert any("OFFSET must be non-negative" in err for err in result.errors)


def test_missing_select_clause_is_an_error() -> None:
    ast = QueryAST(nodes=[WhereNode(condition="1=1")])
    visitor = QueryValidatorVisitor()
    result = ast.accept_visitor(visitor)
    assert any("no SELECT clause" in err for err in result.errors)


def test_reserved_word_column_is_an_error() -> None:
    ast = QueryAST(nodes=[SelectNode(columns=["drop"], table="users")])
    visitor = QueryValidatorVisitor()
    result = ast.accept_visitor(visitor)
    assert any("reserved word" in err for err in result.errors)


def test_where_1_equals_1_is_a_warning() -> None:
    ast = QueryAST(
        nodes=[SelectNode(columns=["id"], table="users"), WhereNode(condition="1=1")]
    )
    visitor = QueryValidatorVisitor()
    result = ast.accept_visitor(visitor)
    assert any("no-op filter" in warn for warn in result.warnings)
