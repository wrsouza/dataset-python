"""Unit tests for LineCountVisitor."""

from __future__ import annotations

from code_metrics_visitor.application.structure import traverse
from code_metrics_visitor.domain.interfaces import (
    ClassNode,
    FunctionNode,
    ModuleNode,
)
from code_metrics_visitor.infrastructure.visitors.line_count import LineCountVisitor


def test_sums_lines_across_functions_and_methods() -> None:
    module = ModuleNode(
        name="m",
        functions=[
            FunctionNode(name="f", line_count=10, branch_count=0, has_docstring=True)
        ],
        classes=[
            ClassNode(
                name="C",
                has_docstring=True,
                methods=[
                    FunctionNode(
                        name="m1", line_count=5, branch_count=0, has_docstring=False
                    )
                ],
            )
        ],
    )

    result = traverse(module, LineCountVisitor())

    assert result.data == {"total_lines": 15, "function_count": 2}


def test_empty_module() -> None:
    module = ModuleNode(name="empty")

    result = traverse(module, LineCountVisitor())

    assert result.data == {"total_lines": 0, "function_count": 0}
