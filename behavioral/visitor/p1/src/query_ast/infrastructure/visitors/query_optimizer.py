"""QueryOptimizerVisitor: rewrites AST hints for better query performance."""

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


class QueryOptimizerVisitor(ASTVisitor):
    """Concrete Visitor that emits optimization suggestions.

    It does NOT mutate the AST; instead it collects hints (index suggestions,
    join reordering advice) into result.data["hints"].
    """

    def __init__(self) -> None:
        self._hints: list[str] = []
        self._join_count = 0
        self._has_where = False
        self._select_table: str = ""

    def visit_select(self, node: SelectNode) -> None:
        self._select_table = node.table
        if not node.columns or node.columns == ["*"]:
            self._hints.append(
                "Avoid SELECT *: fetch only needed columns to reduce I/O."
            )

    def visit_where(self, node: WhereNode) -> None:
        self._has_where = True
        # Suggest index on equality-filter columns
        if "=" in node.condition and "!=" not in node.condition:
            col = node.condition.split("=")[0].strip().split(".")[-1]
            self._hints.append(
                f"Consider an index on '{col}' used in the WHERE predicate."
            )

    def visit_join(self, node: JoinNode) -> None:
        self._join_count += 1
        if self._join_count > 3:
            self._hints.append(
                "More than 3 JOINs detected — consider denormalising or using CTEs."
            )
        if node.join_type.upper() == "LEFT":
            col = node.on_condition.split("=")[-1].strip().split(".")[-1]
            self._hints.append(
                f"Ensure '{col}' in LEFT JOIN ON is indexed on '{node.table}'."
            )

    def visit_order_by(self, node: OrderByNode) -> None:
        cols = [col for col, _ in node.columns]
        self._hints.append(
            f"Add a composite index on ({', '.join(cols)}) "
            "to avoid a filesort for ORDER BY."
        )

    def visit_group_by(self, node: GroupByNode) -> None:
        self._hints.append(
            f"Covering index on ({', '.join(node.columns)}) "
            "will speed up GROUP BY aggregation."
        )

    def visit_limit(self, node: LimitNode) -> None:
        if node.limit > 1000:
            self._hints.append(
                f"LIMIT {node.limit} is large — consider cursor-based pagination."
            )

    @property
    def result(self) -> VisitorResult:
        if not self._has_where:
            self._hints.append(
                "Full table scan detected: add a WHERE clause to filter rows early."
            )
        return VisitorResult(data={"hints": self._hints})


__all__ = ["QueryOptimizerVisitor"]
