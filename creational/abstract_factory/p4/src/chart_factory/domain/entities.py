"""Domain entities and value objects for the Chart Visualization Factory.

SalesDataset is the canonical data structure used by all chart products.
ChartRenderResult wraps a rendered figure together with its metadata.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass(frozen=True)
class SalesRecord:
    """Value object representing a single sales record."""

    month: str
    product: str
    revenue: float
    units_sold: int


@dataclass
class SalesDataset:
    """Entity representing the synthetic sales dataset used in visualisations.

    Provides factory helpers so the Streamlit UI can obtain clean test data
    without depending on any infrastructure.
    """

    records: list[SalesRecord] = field(default_factory=list)

    def to_dataframe(self) -> pd.DataFrame:
        """Convert the dataset to a pandas DataFrame ready for charting."""
        return pd.DataFrame(
            [
                {
                    "month": r.month,
                    "product": r.product,
                    "revenue": r.revenue,
                    "units_sold": r.units_sold,
                }
                for r in self.records
            ]
        )

    @classmethod
    def build_synthetic(cls) -> SalesDataset:
        """Build a deterministic synthetic dataset with 3 products over 6 months.

        Fixed values are intentional — reproducibility beats randomness for a
        teaching dataset where students compare chart outputs side by side.
        """
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        products = [
            ("Widget A", [1_200, 1_500, 1_100, 1_800, 2_000, 1_750], [120, 150, 110, 180, 200, 175]),
            ("Widget B", [800, 950, 1_050, 1_200, 900, 1_100], [80, 95, 105, 120, 90, 110]),
            ("Widget C", [2_000, 1_800, 2_200, 2_500, 2_300, 2_600], [200, 180, 220, 250, 230, 260]),
        ]
        records: list[SalesRecord] = []
        for month in months:
            idx = months.index(month)
            for name, revenues, units in products:
                records.append(
                    SalesRecord(
                        month=month,
                        product=name,
                        revenue=revenues[idx],
                        units_sold=units[idx],
                    )
                )
        return cls(records=records)


@dataclass(frozen=True)
class ChartRenderResult:
    """Value object wrapping a rendered figure with its metadata.

    Decouples the Streamlit UI from the concrete figure types returned
    by different chart libraries.
    """

    library_name: str
    chart_type: str
    figure: object  # plotly.Figure | matplotlib.Figure | altair.Chart

    def __repr__(self) -> str:
        return f"ChartRenderResult(library={self.library_name!r}, type={self.chart_type!r})"
