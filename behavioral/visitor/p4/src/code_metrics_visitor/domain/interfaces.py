"""Domain interfaces: CodeMetricVisitor ABC and CodeElement ABC.

Visitor pattern separates the metric algorithm (line count, cyclomatic
complexity, doc coverage) from the code structure (module/class/
function nodes), enabling new metrics without modifying the nodes.
`ClassNode`/`ModuleNode` also dispatch `accept` down to their children
— the classic Visitor+Composite combination.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class VisitorResult:
    """Aggregated result returned after a visitor traverses the full tree."""

    data: dict[str, object] = field(default_factory=dict)


class CodeMetricVisitor(ABC):
    """Abstract Visitor — one visit_X method per concrete CodeElement type.

    Adding a new metric means creating a new CodeMetricVisitor subclass;
    existing node classes are never modified (OCP).
    """

    @abstractmethod
    def visit_function(self, node: FunctionNode) -> None:
        """Process a single function/method node."""

    @abstractmethod
    def visit_class(self, node: ClassNode) -> None:
        """Process a class node, after its methods have been visited."""

    @abstractmethod
    def visit_module(self, node: ModuleNode) -> None:
        """Process a module node, after its classes/functions have been visited."""

    @property
    def result(self) -> VisitorResult:
        """Return the accumulated result after traversal."""
        return VisitorResult()


class CodeElement(ABC):
    """Abstract Element — every code node exposes accept(visitor).

    Double-dispatch: the node calls the specific visit_X on the visitor,
    so the visitor always knows the concrete type without isinstance checks.
    """

    @abstractmethod
    def accept(self, visitor: CodeMetricVisitor) -> None:
        """Accept a visitor and call the appropriate visit_X method."""


@dataclass
class FunctionNode(CodeElement):
    """A function or method, with metrics already computed for it."""

    name: str
    line_count: int
    branch_count: int
    has_docstring: bool

    def accept(self, visitor: CodeMetricVisitor) -> None:
        visitor.visit_function(self)


@dataclass
class ClassNode(CodeElement):
    """A class — visits each method first, then itself (post-order)."""

    name: str
    has_docstring: bool
    methods: list[FunctionNode] = field(default_factory=list)

    def accept(self, visitor: CodeMetricVisitor) -> None:
        for method in self.methods:
            method.accept(visitor)
        visitor.visit_class(self)


@dataclass
class ModuleNode(CodeElement):
    """A module — visits each class and top-level function, then itself."""

    name: str
    classes: list[ClassNode] = field(default_factory=list)
    functions: list[FunctionNode] = field(default_factory=list)

    def accept(self, visitor: CodeMetricVisitor) -> None:
        for cls in self.classes:
            cls.accept(visitor)
        for function in self.functions:
            function.accept(visitor)
        visitor.visit_module(self)


__all__ = [
    "CodeMetricVisitor",
    "CodeElement",
    "VisitorResult",
    "FunctionNode",
    "ClassNode",
    "ModuleNode",
]
