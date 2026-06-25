"""Shared fixtures for UI Component Decorator tests."""

from __future__ import annotations

import pytest

from ui_components.domain.entities import WidgetSpec


@pytest.fixture
def widget_spec() -> WidgetSpec:
    return WidgetSpec(
        widget_id="w-1",
        label="Sales Summary",
        content="Q2 revenue grew 12%.",
        tags=("sales", "quarterly"),
    )
