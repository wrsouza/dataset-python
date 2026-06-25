"""Content traversal helper — applies a visitor to every node via accept()."""

from __future__ import annotations

from content_export_visitor.domain.interfaces import (
    ContentNode,
    ContentVisitor,
    VisitorResult,
)


def traverse(nodes: list[ContentNode], visitor: ContentVisitor) -> VisitorResult:
    """Visit every node and return the visitor's accumulated result."""
    for node in nodes:
        node.accept(visitor)
    return visitor.result
