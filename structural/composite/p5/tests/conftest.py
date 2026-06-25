"""Shared pytest fixtures for the dashboard component test suite."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def example_definition_path() -> Path:
    """Return the path to the bundled example dashboard definition file."""
    return Path(__file__).resolve().parents[1] / "examples" / "sales_dashboard.json"
