"""Pytest fixtures shared across all P4 test modules."""
from __future__ import annotations

import pytest

from chart_factory.domain.entities import SalesDataset
from chart_factory.infrastructure.factories import (
    AltairChartFactory,
    MatplotlibChartFactory,
    PlotlyChartFactory,
)


@pytest.fixture()
def sales_dataset() -> SalesDataset:
    """Return the canonical synthetic sales dataset."""
    return SalesDataset.build_synthetic()


@pytest.fixture()
def plotly_factory() -> PlotlyChartFactory:
    return PlotlyChartFactory()


@pytest.fixture()
def matplotlib_factory() -> MatplotlibChartFactory:
    return MatplotlibChartFactory()


@pytest.fixture()
def altair_factory() -> AltairChartFactory:
    return AltairChartFactory()
