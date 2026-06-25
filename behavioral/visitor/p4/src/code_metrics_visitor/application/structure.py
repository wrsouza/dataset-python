"""Traversal helper and JSON-to-domain parsing for the module tree."""

from __future__ import annotations

from typing import Any

from code_metrics_visitor.domain.interfaces import (
    ClassNode,
    CodeMetricVisitor,
    FunctionNode,
    ModuleNode,
    VisitorResult,
)


def traverse(module: ModuleNode, visitor: CodeMetricVisitor) -> VisitorResult:
    """Visit the full module tree and return the visitor's accumulated result."""
    module.accept(visitor)
    return visitor.result


def build_function(payload: dict[str, Any]) -> FunctionNode:
    return FunctionNode(
        name=payload["name"],
        line_count=payload.get("line_count", 0),
        branch_count=payload.get("branch_count", 0),
        has_docstring=payload.get("has_docstring", False),
    )


def build_class(payload: dict[str, Any]) -> ClassNode:
    return ClassNode(
        name=payload["name"],
        has_docstring=payload.get("has_docstring", False),
        methods=[build_function(m) for m in payload.get("methods", [])],
    )


def build_module(payload: dict[str, Any]) -> ModuleNode:
    return ModuleNode(
        name=payload["name"],
        classes=[build_class(c) for c in payload.get("classes", [])],
        functions=[build_function(f) for f in payload.get("functions", [])],
    )
