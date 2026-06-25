"""Domain exceptions for the Compression Strategy CLI."""

from __future__ import annotations


class InvalidStrategyError(Exception):
    """Raised when a strategy name is not registered."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Unknown compression strategy '{name}'")
        self.name = name
