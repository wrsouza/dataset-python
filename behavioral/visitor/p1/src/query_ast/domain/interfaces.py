"""Domain interfaces: Visitor ABC and Element ABC for Query AST.

Visitor pattern separates the algorithm (SQL generation, validation, optimization)
from the data structure (AST nodes), enabling new operations without modifying nodes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

# ── Visitor Result ────────────────────────────────────────────────────────────


@dataclass
class VisitorResult:
    """Aggregated result returned after a visitor traverses the full AST."""

    data: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0


# ── Visitor ABC ───────────────────────────────────────────────────────────────


class ASTVisitor(ABC):
    """Abstract Visitor — one visit_X method per concrete Element type.

    Adding a new operation means creating a new ASTVisitor subclass;
    existing ASTNode subclasses are never modified (OCP).
    """

    @abstractmethod
    def visit_select(self, node: SelectNode) -> None:
        """Process a SELECT clause node."""

    @abstractmethod
    def visit_where(self, node: WhereNode) -> None:
        """Process a WHERE clause node."""

    @abstractmethod
    def visit_join(self, node: JoinNode) -> None:
        """Process a JOIN clause node."""

    @abstractmethod
    def visit_order_by(self, node: OrderByNode) -> None:
        """Process an ORDER BY clause node."""

    @abstractmethod
    def visit_group_by(self, node: GroupByNode) -> None:
        """Process a GROUP BY clause node."""

    @abstractmethod
    def visit_limit(self, node: LimitNode) -> None:
        """Process a LIMIT clause node."""

    @property
    def result(self) -> VisitorResult:
        """Return the accumulated result after traversal."""
        return VisitorResult()


# ── Element ABC ───────────────────────────────────────────────────────────────


class ASTNode(ABC):
    """Abstract Element — every AST node exposes accept(visitor).

    Double-dispatch: the node calls the specific visit_X on the visitor,
    so the visitor always knows the concrete type without isinstance checks.
    """

    @abstractmethod
    def accept(self, visitor: ASTVisitor) -> None:
        """Accept a visitor and call the appropriate visit_X method."""


# ── Concrete Elements (forward-declared for the Visitor ABC above) ─────────


@dataclass
class SelectNode(ASTNode):
    """SELECT clause: list of columns/expressions to project."""

    columns: list[str]
    table: str

    def accept(self, visitor: ASTVisitor) -> None:
        visitor.visit_select(self)


@dataclass
class WhereNode(ASTNode):
    """WHERE clause: filter predicate as a raw condition string."""

    condition: str

    def accept(self, visitor: ASTVisitor) -> None:
        visitor.visit_where(self)


@dataclass
class JoinNode(ASTNode):
    """JOIN clause: join type, target table, and ON condition."""

    join_type: str  # INNER, LEFT, RIGHT, FULL
    table: str
    on_condition: str

    def accept(self, visitor: ASTVisitor) -> None:
        visitor.visit_join(self)


@dataclass
class OrderByNode(ASTNode):
    """ORDER BY clause: list of (column, direction) pairs."""

    columns: list[tuple[str, str]]  # (column_name, ASC|DESC)

    def accept(self, visitor: ASTVisitor) -> None:
        visitor.visit_order_by(self)


@dataclass
class GroupByNode(ASTNode):
    """GROUP BY clause: list of columns to group on."""

    columns: list[str]

    def accept(self, visitor: ASTVisitor) -> None:
        visitor.visit_group_by(self)


@dataclass
class LimitNode(ASTNode):
    """LIMIT clause: maximum number of rows and optional offset."""

    limit: int
    offset: int = 0

    def accept(self, visitor: ASTVisitor) -> None:
        visitor.visit_limit(self)


__all__ = [
    "ASTVisitor",
    "ASTNode",
    "VisitorResult",
    "SelectNode",
    "WhereNode",
    "JoinNode",
    "OrderByNode",
    "GroupByNode",
    "LimitNode",
]
