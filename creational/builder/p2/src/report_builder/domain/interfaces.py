"""Abstract interfaces for the Report Builder pattern."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Self

from report_builder.domain.entities import ChartSpec, DataTable, Report


class ReportBuilder(ABC):
    """Builder interface — all concrete builders implement these steps.

    OCP: new formats are added by subclassing, not modifying this ABC.
    """

    @abstractmethod
    def set_title(self, title: str) -> Self: ...

    @abstractmethod
    def add_header(self, text: str) -> Self: ...

    @abstractmethod
    def add_data_table(self, table: DataTable) -> Self: ...

    @abstractmethod
    def add_chart(self, chart: ChartSpec) -> Self: ...

    @abstractmethod
    def add_footer(self, text: str) -> Self: ...

    @abstractmethod
    def build(self) -> Report: ...
