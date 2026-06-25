"""ObjectStructure: QueryAST manages a collection of ASTNodes and drives traversal."""

from __future__ import annotations

from dataclasses import dataclass, field

from query_ast.domain.interfaces import ASTNode, ASTVisitor, VisitorResult


@dataclass
class QueryAST:
    """Object Structure — holds an ordered list of ASTNodes and drives traversal.

    Clients build the AST by adding nodes, then call accept_visitor() to run
    any ASTVisitor over the entire structure.  The visitor accumulates its
    result internally; QueryAST retrieves it via visitor.result.
    """

    nodes: list[ASTNode] = field(default_factory=list)

    def add_node(self, node: ASTNode) -> QueryAST:
        """Append a node and return self for fluent chaining."""
        self.nodes.append(node)
        return self

    def accept_visitor(self, visitor: ASTVisitor) -> VisitorResult:
        """Traverse all nodes in insertion order, letting the visitor process each."""
        for node in self.nodes:
            node.accept(visitor)
        return visitor.result


__all__ = ["QueryAST"]
