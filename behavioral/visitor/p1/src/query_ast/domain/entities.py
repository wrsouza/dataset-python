"""Domain entities and value objects for the Query AST context.

These are pure data holders with no dependency on FastAPI, visitors, or
infrastructure — they describe the vocabulary of the domain itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class OperationType(StrEnum):
    """The set of operations a client may request over a QueryAST.

    Adding a new ConcreteVisitor (infrastructure/) means adding a new member
    here and wiring it in the use case factory — the AST nodes themselves
    stay untouched (Open/Closed Principle).
    """

    EXPLAIN = "explain"
    OPTIMIZE = "optimize"
    VALIDATE = "validate"
    GENERATE_SQL = "generate_sql"


@dataclass(frozen=True)
class AnalysisReport:
    """Outcome of running one operation over a QueryAST.

    A thin domain-level wrapper around the visitor's raw result, keeping the
    API response shape decoupled from VisitorResult's internal field names.
    """

    operation: OperationType
    is_valid: bool
    data: dict[str, object]
    errors: list[str]
    warnings: list[str]


__all__ = ["OperationType", "AnalysisReport"]
