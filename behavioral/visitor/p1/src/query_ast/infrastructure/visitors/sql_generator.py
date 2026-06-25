"""SQLGeneratorVisitor: builds a SQL string from a traversed QueryAST."""

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


class SQLGeneratorVisitor(ASTVisitor):
    """Concrete Visitor that generates a SQL SELECT statement.

    Each visit_X appends its SQL fragment; result.data["sql"] holds
    the final assembled statement.
    """

    def __init__(self) -> None:
        self._select: str = ""
        self._joins: list[str] = []
        self._where: str = ""
        self._group_by: str = ""
        self._order_by: str = ""
        self._limit: str = ""

    # ── visit_X methods ───────────────────────────────────────────────────────

    def visit_select(self, node: SelectNode) -> None:
        cols = ", ".join(node.columns) if node.columns else "*"
        self._select = f"SELECT {cols} FROM {node.table}"

    def visit_where(self, node: WhereNode) -> None:
        self._where = f"WHERE {node.condition}"

    def visit_join(self, node: JoinNode) -> None:
        self._joins.append(f"{node.join_type} JOIN {node.table} ON {node.on_condition}")

    def visit_order_by(self, node: OrderByNode) -> None:
        parts = [f"{col} {direction}" for col, direction in node.columns]
        self._order_by = f"ORDER BY {', '.join(parts)}"

    def visit_group_by(self, node: GroupByNode) -> None:
        self._group_by = f"GROUP BY {', '.join(node.columns)}"

    def visit_limit(self, node: LimitNode) -> None:
        self._limit = f"LIMIT {node.limit}"
        if node.offset:
            self._limit += f" OFFSET {node.offset}"

    # ── result ────────────────────────────────────────────────────────────────

    @property
    def result(self) -> VisitorResult:
        parts = [self._select]
        parts.extend(self._joins)
        if self._where:
            parts.append(self._where)
        if self._group_by:
            parts.append(self._group_by)
        if self._order_by:
            parts.append(self._order_by)
        if self._limit:
            parts.append(self._limit)
        sql = "\n".join(p for p in parts if p)
        return VisitorResult(data={"sql": sql})


__all__ = ["SQLGeneratorVisitor"]
