"""DocCoverageVisitor: tracks what fraction of functions/classes/modules
have a docstring."""

from __future__ import annotations

from code_metrics_visitor.domain.interfaces import (
    ClassNode,
    CodeMetricVisitor,
    FunctionNode,
    ModuleNode,
    VisitorResult,
)


class DocCoverageVisitor(CodeMetricVisitor):
    def __init__(self) -> None:
        self._documented = 0
        self._total = 0

    def visit_function(self, node: FunctionNode) -> None:
        self._record(node.has_docstring)

    def visit_class(self, node: ClassNode) -> None:
        self._record(node.has_docstring)

    def visit_module(self, node: ModuleNode) -> None:
        pass

    def _record(self, has_docstring: bool) -> None:
        self._total += 1
        if has_docstring:
            self._documented += 1

    @property
    def result(self) -> VisitorResult:
        coverage = (self._documented / self._total) if self._total else 0.0
        return VisitorResult(
            data={
                "documented": self._documented,
                "total": self._total,
                "coverage": round(coverage, 4),
            }
        )
