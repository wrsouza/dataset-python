"""Domain exceptions for the ML Model Strategy demo."""

from __future__ import annotations


class InvalidStrategyError(Exception):
    """Raised when a model name is not registered."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Unknown model strategy '{name}'")
        self.name = name


class FeatureMismatchError(Exception):
    """Raised when a model receives the wrong number of input features."""

    def __init__(self, expected: int, got: int) -> None:
        super().__init__(f"Expected {expected} features, got {got}")
        self.expected = expected
        self.got = got
