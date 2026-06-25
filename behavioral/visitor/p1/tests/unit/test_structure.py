"""Unit tests for the QueryAST object structure (Visitor traversal driver)."""

from __future__ import annotations

from query_ast.application.structure import QueryAST
from query_ast.domain.interfaces import ASTVisitor, SelectNode, VisitorResult, WhereNode


class _RecordingVisitor(ASTVisitor):
    """Test double that records the order in which nodes were visited."""

    def __init__(self) -> None:
        self.visited: list[str] = []

    def visit_select(self, node: SelectNode) -> None:
        self.visited.append("select")

    def visit_where(self, node: WhereNode) -> None:
        self.visited.append("where")

    def visit_join(self, node: object) -> None:
        self.visited.append("join")

    def visit_order_by(self, node: object) -> None:
        self.visited.append("order_by")

    def visit_group_by(self, node: object) -> None:
        self.visited.append("group_by")

    def visit_limit(self, node: object) -> None:
        self.visited.append("limit")

    @property
    def result(self) -> VisitorResult:
        return VisitorResult(data={"visited": self.visited})


def test_add_node_returns_self_for_chaining() -> None:
    ast = QueryAST()
    returned = ast.add_node(SelectNode(columns=["id"], table="users"))
    assert returned is ast
    assert len(ast.nodes) == 1


def test_accept_visitor_traverses_in_insertion_order(full_query_ast: QueryAST) -> None:
    visitor = _RecordingVisitor()
    result = full_query_ast.accept_visitor(visitor)
    assert result.data["visited"] == [
        "select",
        "join",
        "where",
        "group_by",
        "order_by",
        "limit",
    ]


def test_accept_visitor_on_empty_ast_returns_empty_result() -> None:
    ast = QueryAST()
    visitor = _RecordingVisitor()
    result = ast.accept_visitor(visitor)
    assert result.data["visited"] == []
