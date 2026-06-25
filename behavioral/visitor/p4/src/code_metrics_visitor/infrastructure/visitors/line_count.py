"""LineCountVisitor: sums line_count across every function/method."""

from __future__ import annotations

from code_metrics_visitor.domain.interfaces import (
    ClassNode,
    CodeMetricVisitor,
    FunctionNode,
    ModuleNode,
    VisitorResult,
)


class LineCountVisitor(CodeMetricVisitor):
    def __init__(self) -> None:
        self._total_lines = 0
        self._function_count = 0

    def visit_function(self, node: FunctionNode) -> None:
        self._total_lines += node.line_count
        self._function_count += 1

    def visit_class(self, node: ClassNode) -> None:
        pass

    def visit_module(self, node: ModuleNode) -> None:
        pass

    @property
    def result(self) -> VisitorResult:
        return VisitorResult(
            data={
                "total_lines": self._total_lines,
                "function_count": self._function_count,
            }
        )
