"""ComplexityVisitor: sums branch counts and flags overly complex functions."""

from __future__ import annotations

from code_metrics_visitor.domain.interfaces import (
    ClassNode,
    CodeMetricVisitor,
    FunctionNode,
    ModuleNode,
    VisitorResult,
)

_COMPLEXITY_THRESHOLD = 10


class ComplexityVisitor(CodeMetricVisitor):
    def __init__(self) -> None:
        self._total_branches = 0
        self._complex_functions: list[str] = []

    def visit_function(self, node: FunctionNode) -> None:
        self._total_branches += node.branch_count
        if node.branch_count > _COMPLEXITY_THRESHOLD:
            self._complex_functions.append(node.name)

    def visit_class(self, node: ClassNode) -> None:
        pass

    def visit_module(self, node: ModuleNode) -> None:
        pass

    @property
    def result(self) -> VisitorResult:
        return VisitorResult(
            data={
                "total_branches": self._total_branches,
                "complex_functions": list(self._complex_functions),
            }
        )
