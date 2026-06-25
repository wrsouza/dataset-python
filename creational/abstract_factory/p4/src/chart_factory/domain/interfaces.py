"""Abstract interfaces for the Chart Visualization Factory pattern.

This module defines the AbstractFactory and AbstractProduct roles.
All concrete factories and chart products must implement these contracts.

OCP: add a new chart library by creating a new ConcreteFactory subclass.
DIP: the Streamlit app depends on ChartFactory (abstraction), never on concrete classes.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import pandas as pd


class LineChart(ABC):
    """AbstractProduct: line chart component interface."""

    @abstractmethod
    def render(self, data: pd.DataFrame) -> Any:
        """Render a line chart from the given DataFrame and return the figure object."""
        ...

    @abstractmethod
    def get_library_name(self) -> str:
        """Return the name of the underlying chart library."""
        ...


class BarChart(ABC):
    """AbstractProduct: bar chart component interface."""

    @abstractmethod
    def render(self, data: pd.DataFrame) -> Any:
        """Render a bar chart from the given DataFrame and return the figure object."""
        ...

    @abstractmethod
    def get_library_name(self) -> str:
        """Return the name of the underlying chart library."""
        ...


class PieChart(ABC):
    """AbstractProduct: pie / donut chart component interface."""

    @abstractmethod
    def render(self, data: pd.DataFrame) -> Any:
        """Render a pie chart from the given DataFrame and return the figure object."""
        ...

    @abstractmethod
    def get_library_name(self) -> str:
        """Return the name of the underlying chart library."""
        ...


class ChartFactory(ABC):
    """AbstractFactory: defines the interface for creating chart families.

    Each ConcreteFactory produces charts rendered by the same underlying library,
    ensuring visual consistency within a family.

    OCP: add a new library (e.g. Bokeh) by subclassing ChartFactory — zero edits
         to existing factories, use cases or the Streamlit UI.
    DIP: the Streamlit app receives a ChartFactory and never imports concrete classes.
    """

    @abstractmethod
    def create_line_chart(self) -> LineChart:
        """Create a library-specific line chart."""
        ...

    @abstractmethod
    def create_bar_chart(self) -> BarChart:
        """Create a library-specific bar chart."""
        ...

    @abstractmethod
    def create_pie_chart(self) -> PieChart:
        """Create a library-specific pie chart."""
        ...

    @abstractmethod
    def get_library_name(self) -> str:
        """Return the human-readable name of the chart library."""
        ...
