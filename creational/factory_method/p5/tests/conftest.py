"""Shared pytest fixtures for the Serializer Factory test suite."""

from __future__ import annotations

import pytest


@pytest.fixture
def sample_records() -> list[dict[str, object]]:
    """A small representative list of records used across tests."""
    return [
        {"id": 1, "name": "Alice", "role": "engineer", "salary": 95000},
        {"id": 2, "name": "Bob", "role": "designer", "salary": 87000},
        {"id": 3, "name": "Carol", "role": "manager", "salary": 105000},
    ]
