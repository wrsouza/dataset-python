"""Domain exceptions for the Code Metrics Visitor system."""

from __future__ import annotations


class InvalidMetricError(Exception):
    """Raised when a metric name is not registered."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Unknown metric '{name}'")
        self.name = name
