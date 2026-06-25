"""QueryValidatorVisitor: checks semantic rules on a QueryAST."""

from __future__ import annotations

from query_ast.domain.interfaces import (
    ASTVisitor,
    GroupByNode,
    JoinNode,
    LimitNode,
    OrderByNode,
    SelectNode,
    VisitorResult,
    WhereNode,
)

_RESERVED_WORDS = frozenset({"drop", "delete", "truncate", "insert", "update"})
_VALID_JOIN_TYPES = frozenset({"INNER", "LEFT", "RIGHT", "FULL"})


class QueryValidatorVisitor(ASTVisitor):
    """Concrete Visitor that validates query semantics without modifying AST nodes.

    Errors block execution; warnings are informational.
    """

    def __init__(self) -> None:
        self._errors: list[str] = []
        self._warnings: list[str] = []
        self._has_select = False

    def visit_select(self, node: SelectNode) -> None:
        self._has_select = True
        if not node.table:
            self._errors.append("SELECT requires a FROM table.")
        if not node.columns:
            self._warnings.append(
                "SELECT * is discouraged; specify columns explicitly."
            )
        for col in node.columns:
            if col.lower().split()[0] in _RESERVED_WORDS:
                self._errors.append(f"Column name '{col}' contains a reserved word.")

    def visit_where(self, node: WhereNode) -> None:
        if not node.condition.strip():
            self._errors.append("WHERE clause has an empty condition.")
        if "1=1" in node.condition.replace(" ", ""):
            self._warnings.append("WHERE 1=1 is a no-op filter.")

    def visit_join(self, node: JoinNode) -> None:
        if node.join_type.upper() not in _VALID_JOIN_TYPES:
            self._errors.append(
                f"Invalid JOIN type '{node.join_type}'. "
                f"Allowed: {sorted(_VALID_JOIN_TYPES)}"
            )
        if not node.on_condition.strip():
            self._errors.append(f"JOIN on table '{node.table}' has no ON condition.")

    def visit_order_by(self, node: OrderByNode) -> None:
        for col, direction in node.columns:
            if direction.upper() not in ("ASC", "DESC"):
                self._errors.append(
                    f"ORDER BY column '{col}' has invalid direction '{direction}'."
                )

    def visit_group_by(self, node: GroupByNode) -> None:
        if not node.columns:
            self._errors.append("GROUP BY clause has no columns.")

    def visit_limit(self, node: LimitNode) -> None:
        if node.limit <= 0:
            self._errors.append(f"LIMIT must be positive, got {node.limit}.")
        if node.offset < 0:
            self._errors.append(f"OFFSET must be non-negative, got {node.offset}.")

    @property
    def result(self) -> VisitorResult:
        if not self._has_select:
            self._errors.append("Query has no SELECT clause.")
        return VisitorResult(errors=self._errors, warnings=self._warnings)


__all__ = ["QueryValidatorVisitor"]
