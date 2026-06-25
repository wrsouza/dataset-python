"""Shared pytest fixtures for the build task test suite."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def example_definition_path() -> Path:
    """Return the path to the bundled example YAML definition file."""
    return Path(__file__).resolve().parents[1] / "examples" / "build_all.yml"
