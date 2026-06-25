"""Unit tests for ComplexityVisitor."""

from __future__ import annotations

from code_metrics_visitor.application.structure import traverse
from code_metrics_visitor.domain.interfaces import FunctionNode, ModuleNode
from code_metrics_visitor.infrastructure.visitors.complexity import ComplexityVisitor


def test_sums_branches_and_flags_complex_functions() -> None:
    module = ModuleNode(
        name="m",
        functions=[
            FunctionNode(
                name="simple", line_count=5, branch_count=2, has_docstring=True
            ),
            FunctionNode(
                name="tangled", line_count=50, branch_count=15, has_docstring=False
            ),
        ],
    )

    result = traverse(module, ComplexityVisitor())

    assert result.data["total_branches"] == 17
    assert result.data["complex_functions"] == ["tangled"]


def test_no_complex_functions() -> None:
    module = ModuleNode(
        name="m",
        functions=[
            FunctionNode(name="f", line_count=5, branch_count=1, has_docstring=True)
        ],
    )

    result = traverse(module, ComplexityVisitor())

    assert result.data["complex_functions"] == []
