"""Domain exceptions for the Data Transformation Visitor system."""

from __future__ import annotations


class InvalidTransformationError(Exception):
    """Raised when a transformation name is not registered."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Unknown transformation '{name}'")
        self.name = name


class InvalidColumnTypeError(Exception):
    """Raised when a column's `type` field is not recognised."""

    def __init__(self, column_type: str) -> None:
        super().__init__(f"Unknown column type '{column_type}'")
        self.column_type = column_type
