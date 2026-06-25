"""Composite and Leaf implementations of OrgUnit backed by ORM models."""

from __future__ import annotations

from decimal import Decimal

from organization.domain.interfaces import EmployeeData, OrgUnit
from organization.infrastructure.models import EmployeeModel, OrgUnitModel


class EmployeeLeaf(OrgUnit):
    """Leaf: a single employee with no children.

    Satisfies LSP — every method returns the correct type/value for
    a single-person unit so callers need no isinstance() checks.
    """

    def __init__(self, model: EmployeeModel) -> None:
        self._model = model

    def get_headcount(self) -> int:
        return 1

    def get_total_salary(self) -> Decimal:
        return self._model.salary

    def get_members(self) -> list[EmployeeData]:
        return [EmployeeData(self._model.name, self._model.title, self._model.salary)]

    def display(self, indent: int = 0) -> str:
        prefix = "  " * indent
        return f"{prefix}👤 {self._model.name} ({self._model.title}) — ${self._model.salary}"


class CompositeOrgUnit(OrgUnit):
    """Composite: a unit that contains children (other OrgUnits or Employees).

    Delegates all recursive operations to children, accumulating results.
    OCP: new unit types extend this class; no modification needed here.
    """

    def __init__(self, model: OrgUnitModel, children: list[OrgUnit]) -> None:
        self._model = model
        self._children: list[OrgUnit] = children

    def add_child(self, child: OrgUnit) -> None:
        self._children.append(child)

    def remove_child(self, child: OrgUnit) -> None:
        self._children.remove(child)

    def get_children(self) -> list[OrgUnit]:
        return list(self._children)

    def get_headcount(self) -> int:
        return sum(child.get_headcount() for child in self._children)

    def get_total_salary(self) -> Decimal:
        return sum(
            (child.get_total_salary() for child in self._children), Decimal("0")
        )

    def get_members(self) -> list[EmployeeData]:
        members: list[EmployeeData] = []
        for child in self._children:
            members.extend(child.get_members())
        return members

    def display(self, indent: int = 0) -> str:
        prefix = "  " * indent
        lines = [f"{prefix}📁 {self._model.name} [{self._model.unit_type}]"]
        for child in self._children:
            lines.append(child.display(indent + 1))
        return "\n".join(lines)


def build_composite_tree(unit_model: OrgUnitModel) -> OrgUnit:
    """Factory: recursively converts ORM models into the Composite tree.

    Separation of concerns: ORM loading stays in infrastructure; the
    domain objects (Leaf/Composite) remain persistence-agnostic.
    """
    children: list[OrgUnit] = []

    for employee in unit_model.employees:
        children.append(EmployeeLeaf(employee))

    for child_unit in unit_model.children:
        children.append(build_composite_tree(child_unit))

    return CompositeOrgUnit(unit_model, children)
