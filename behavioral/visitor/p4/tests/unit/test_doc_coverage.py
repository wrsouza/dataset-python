"""Unit tests for DocCoverageVisitor."""

from __future__ import annotations

from code_metrics_visitor.application.structure import traverse
from code_metrics_visitor.domain.interfaces import ClassNode, FunctionNode, ModuleNode
from code_metrics_visitor.infrastructure.visitors.doc_coverage import (
    DocCoverageVisitor,
)


def test_computes_coverage_across_functions_and_classes() -> None:
    module = ModuleNode(
        name="m",
        functions=[
            FunctionNode(name="f1", line_count=1, branch_count=0, has_docstring=True),
            FunctionNode(name="f2", line_count=1, branch_count=0, has_docstring=False),
        ],
        classes=[ClassNode(name="C", has_docstring=True)],
    )

    result = traverse(module, DocCoverageVisitor())

    assert result.data == {"documented": 2, "total": 3, "coverage": round(2 / 3, 4)}


def test_coverage_is_zero_when_nothing_to_document() -> None:
    module = ModuleNode(name="empty")

    result = traverse(module, DocCoverageVisitor())

    assert result.data == {"documented": 0, "total": 0, "coverage": 0.0}
