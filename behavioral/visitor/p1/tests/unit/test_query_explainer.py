"""Unit tests for QueryExplainerVisitor."""

from __future__ import annotations

from query_ast.application.structure import QueryAST
from query_ast.infrastructure.visitors import QueryExplainerVisitor


def test_explains_simple_select(simple_select_ast: QueryAST) -> None:
    visitor = QueryExplainerVisitor()
    result = simple_select_ast.accept_visitor(visitor)
    assert "id, name" in result.data["explanation"]
    assert "users" in result.data["explanation"]


def test_explains_full_query_mentions_every_clause(full_query_ast: QueryAST) -> None:
    visitor = QueryExplainerVisitor()
    result = full_query_ast.accept_visitor(visitor)
    explanation = result.data["explanation"]
    assert "Fetch" in explanation
    assert "Combine" in explanation
    assert "Filter rows" in explanation
    assert "Group results" in explanation
    assert "Sort results" in explanation
    assert "Return at most 50 rows" in explanation


def test_explain_result_is_always_valid(simple_select_ast: QueryAST) -> None:
    visitor = QueryExplainerVisitor()
    result = simple_select_ast.accept_visitor(visitor)
    assert result.is_valid is True


def test_explains_select_star_when_no_columns() -> None:
    ast = QueryAST()
    from query_ast.domain.interfaces import SelectNode

    ast.add_node(SelectNode(columns=[], table="orders"))
    visitor = QueryExplainerVisitor()
    result = ast.accept_visitor(visitor)
    assert "all columns" in result.data["explanation"]
