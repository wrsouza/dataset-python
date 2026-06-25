"""Domain interfaces: ColumnVisitor ABC and DataColumn ABC.

Visitor pattern separates the transformation algorithm (normalize,
anonymize, summarize) from the data structure (numeric/text/date
columns), enabling new transformations without modifying the column
classes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class VisitorResult:
    """Aggregated result returned after a visitor traverses every column."""

    columns: dict[str, Any] = field(default_factory=dict)


class ColumnVisitor(ABC):
    """Abstract Visitor — one visit_X method per concrete DataColumn type.

    Adding a new transformation means creating a new ColumnVisitor
    subclass; existing column classes are never modified (OCP).
    """

    @abstractmethod
    def visit_numeric(self, column: NumericColumn) -> None:
        """Process a numeric column."""

    @abstractmethod
    def visit_text(self, column: TextColumn) -> None:
        """Process a text column."""

    @abstractmethod
    def visit_date(self, column: DateColumn) -> None:
        """Process a date (ISO string) column."""

    @property
    def result(self) -> VisitorResult:
        """Return the accumulated result after traversal."""
        return VisitorResult()


class DataColumn(ABC):
    """Abstract Element — every column exposes accept(visitor) and a name."""

    name: str

    @abstractmethod
    def accept(self, visitor: ColumnVisitor) -> None:
        """Accept a visitor and call the appropriate visit_X method."""


@dataclass
class NumericColumn(DataColumn):
    name: str
    values: list[float]

    def accept(self, visitor: ColumnVisitor) -> None:
        visitor.visit_numeric(self)


@dataclass
class TextColumn(DataColumn):
    name: str
    values: list[str]

    def accept(self, visitor: ColumnVisitor) -> None:
        visitor.visit_text(self)


@dataclass
class DateColumn(DataColumn):
    name: str
    values: list[str]  # ISO "YYYY-MM-DD" strings

    def accept(self, visitor: ColumnVisitor) -> None:
        visitor.visit_date(self)


__all__ = [
    "ColumnVisitor",
    "DataColumn",
    "VisitorResult",
    "NumericColumn",
    "TextColumn",
    "DateColumn",
]
