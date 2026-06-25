"""Component ABC for the Composite pattern — OrgUnit hierarchy."""

from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal


class OrgUnit(ABC):
    """Abstract Component: defines the uniform interface for all org nodes.

    Both leaves (Employee) and composites (Team, Department, Company)
    implement this interface, enabling clients to treat them uniformly.
    LSP is guaranteed because every subclass fulfills the same contract.
    """

    @abstractmethod
    def get_headcount(self) -> int:
        """Return the total number of employees under this unit."""
        ...

    @abstractmethod
    def get_total_salary(self) -> Decimal:
        """Return the sum of all employee salaries under this unit."""
        ...

    @abstractmethod
    def get_members(self) -> list["EmployeeData"]:
        """Return a flat list of all employees under this unit."""
        ...

    @abstractmethod
    def display(self, indent: int = 0) -> str:
        """Render a human-readable tree representation of this unit."""
        ...


class EmployeeData:
    """Value object representing a single employee (used by get_members)."""

    def __init__(self, name: str, title: str, salary: Decimal) -> None:
        self.name = name
        self.title = title
        self.salary = salary

    def __repr__(self) -> str:
        return f"EmployeeData(name={self.name!r}, title={self.title!r})"
