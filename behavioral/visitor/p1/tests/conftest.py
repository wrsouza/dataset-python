"""Shared fixtures for Query AST Visitor tests."""

from __future__ import annotations

import pytest

from query_ast.application.structure import QueryAST
from query_ast.domain.interfaces import (
    GroupByNode,
    JoinNode,
    LimitNode,
    OrderByNode,
    SelectNode,
    WhereNode,
)


@pytest.fixture
def simple_select_ast() -> QueryAST:
    """A minimal AST: SELECT id, name FROM users."""
    return QueryAST(nodes=[SelectNode(columns=["id", "name"], table="users")])


@pytest.fixture
def full_query_ast() -> QueryAST:
    """A representative AST exercising every node type."""
    return QueryAST(
        nodes=[
            SelectNode(columns=["u.id", "u.name", "o.total"], table="users u"),
            JoinNode(
                join_type="LEFT", table="orders o", on_condition="u.id = o.user_id"
            ),
            WhereNode(condition="u.active = true"),
            GroupByNode(columns=["u.id"]),
            OrderByNode(columns=[("u.name", "ASC")]),
            LimitNode(limit=50, offset=0),
        ]
    )
