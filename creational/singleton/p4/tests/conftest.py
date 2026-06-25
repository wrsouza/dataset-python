"""Shared pytest fixtures for the Structured Logger test suite."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from src.logger.infrastructure.singleton import reset_singleton_for_tests


@pytest.fixture(autouse=True)
def _reset_logger_singleton() -> Iterator[None]:
    """Ensure each test starts with a fresh StructuredLogger instance.

    Without this, the singleton created by one test would leak into the
    next test (shared global state is the whole point of a singleton —
    but tests need isolation).
    """
    reset_singleton_for_tests()
    yield
    reset_singleton_for_tests()
