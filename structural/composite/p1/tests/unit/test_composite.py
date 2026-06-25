"""Unit tests for the Composite pattern — no database required."""

from __future__ import annotations

from decimal import Decimal

import pytest

from organization.domain.interfaces import EmployeeData, OrgUnit
from organization.infrastructure.models import EmployeeModel, OrgUnitModel


def make_employee_model(
    id_: int, name: str, title: str, salary: str, unit_id: int = 1
) -> EmployeeModel:
    e = EmployeeModel()
    e.id = id_
    e.name = name
    e.title = title
    e.salary = Decimal(salary)
    e.unit_id = unit_id
    return e


def make_unit_model(
    id_: int,
    name: str,
    unit_type: str,
    employees: list[EmployeeModel] | None = None,
    children: list[OrgUnitModel] | None = None,
    parent_id: int | None = None,
) -> OrgUnitModel:
    u = OrgUnitModel()
    u.id = id_
    u.name = name
    u.unit_type = unit_type
    u.parent_id = parent_id
    u.employees = employees or []
    u.children = children or []
    return u


# ── EmployeeLeaf tests ────────────────────────────────────────────────────────

class TestEmployeeLeaf:
    def _make_leaf(self, salary: str = "5000") -> OrgUnit:
        from organization.infrastructure.composite import EmployeeLeaf

        model = make_employee_model(1, "Alice", "Engineer", salary)
        return EmployeeLeaf(model)

    def test_headcount_is_one(self) -> None:
        leaf = self._make_leaf()
        assert leaf.get_headcount() == 1

    def test_total_salary_equals_own_salary(self) -> None:
        leaf = self._make_leaf("7500.00")
        assert leaf.get_total_salary() == Decimal("7500.00")

    def test_get_members_returns_single_item(self) -> None:
        leaf = self._make_leaf()
        members = leaf.get_members()
        assert len(members) == 1
        assert members[0].name == "Alice"

    def test_display_contains_name(self) -> None:
        leaf = self._make_leaf()
        assert "Alice" in leaf.display()

    def test_display_indent(self) -> None:
        leaf = self._make_leaf()
        displayed = leaf.display(indent=2)
        assert displayed.startswith("    ")


# ── CompositeOrgUnit tests ────────────────────────────────────────────────────

class TestCompositeOrgUnit:
    def _build_company_tree(self) -> OrgUnit:
        from organization.infrastructure.composite import build_composite_tree

        eng1 = make_employee_model(1, "Alice", "Senior Dev", "10000")
        eng2 = make_employee_model(2, "Bob", "Junior Dev", "6000")
        team_model = make_unit_model(2, "Backend Team", "team", employees=[eng1, eng2])

        mgr = make_employee_model(3, "Carol", "VP Eng", "20000")
        dept_model = make_unit_model(
            3, "Engineering", "department", employees=[mgr], children=[team_model]
        )

        admin = make_employee_model(4, "Dave", "CEO", "30000")
        company_model = make_unit_model(
            1, "Acme Corp", "company", employees=[admin], children=[dept_model]
        )

        return build_composite_tree(company_model)

    def test_headcount_sums_entire_tree(self) -> None:
        company = self._build_company_tree()
        # 4 employees: Alice, Bob, Carol, Dave
        assert company.get_headcount() == 4

    def test_total_salary_sums_recursively(self) -> None:
        company = self._build_company_tree()
        expected = Decimal("10000") + Decimal("6000") + Decimal("20000") + Decimal("30000")
        assert company.get_total_salary() == expected

    def test_get_members_returns_all_employees(self) -> None:
        company = self._build_company_tree()
        members = company.get_members()
        assert len(members) == 4
        names = {m.name for m in members}
        assert names == {"Alice", "Bob", "Carol", "Dave"}

    def test_display_shows_all_levels(self) -> None:
        company = self._build_company_tree()
        display = company.display()
        assert "Acme Corp" in display
        assert "Engineering" in display
        assert "Backend Team" in display
        assert "Alice" in display

    def test_empty_composite_headcount_is_zero(self) -> None:
        from organization.infrastructure.composite import CompositeOrgUnit

        unit = make_unit_model(99, "Empty Dept", "department")
        composite = CompositeOrgUnit(unit, [])
        assert composite.get_headcount() == 0

    def test_empty_composite_salary_is_zero(self) -> None:
        from organization.infrastructure.composite import CompositeOrgUnit

        unit = make_unit_model(99, "Empty Dept", "department")
        composite = CompositeOrgUnit(unit, [])
        assert composite.get_total_salary() == Decimal("0")

    def test_single_leaf_composite(self) -> None:
        from organization.infrastructure.composite import EmployeeLeaf, CompositeOrgUnit

        emp = make_employee_model(1, "Solo", "CTO", "50000")
        leaf = EmployeeLeaf(emp)
        unit = make_unit_model(1, "Solo Corp", "company")
        composite = CompositeOrgUnit(unit, [leaf])
        assert composite.get_headcount() == 1
        assert composite.get_total_salary() == Decimal("50000")

    def test_deep_tree_recursion(self) -> None:
        """Verify recursive operations work on deeply nested structures (5 levels)."""
        from organization.infrastructure.composite import build_composite_tree

        # Build 5-level deep tree
        bottom_emp = make_employee_model(1, "Bottom", "Intern", "1000")
        level5 = make_unit_model(5, "L5", "team", employees=[bottom_emp])
        level4 = make_unit_model(4, "L4", "team", children=[level5])
        level3 = make_unit_model(3, "L3", "department", children=[level4])
        level2 = make_unit_model(2, "L2", "department", children=[level3])
        level1 = make_unit_model(1, "L1", "company", children=[level2])

        root = build_composite_tree(level1)
        assert root.get_headcount() == 1
        assert root.get_total_salary() == Decimal("1000")

    def test_lsp_leaf_and_composite_are_interchangeable(self) -> None:
        """LSP: client code treats EmployeeLeaf and CompositeOrgUnit identically."""
        from organization.infrastructure.composite import build_composite_tree, EmployeeLeaf

        emp1 = make_employee_model(1, "A", "Dev", "1000")
        emp2 = make_employee_model(2, "B", "Dev", "2000")
        leaf1 = EmployeeLeaf(emp1)
        leaf2 = EmployeeLeaf(emp2)

        unit = make_unit_model(1, "Team", "team")
        from organization.infrastructure.composite import CompositeOrgUnit
        composite = CompositeOrgUnit(unit, [leaf1, leaf2])

        # Both leaf and composite answer the same interface calls
        units: list[OrgUnit] = [leaf1, composite]
        total_headcount = sum(u.get_headcount() for u in units)
        total_salary = sum(u.get_total_salary() for u in units)

        # leaf1 headcount=1, composite headcount=2
        assert total_headcount == 3
        assert total_salary == Decimal("4000")


# ── Composite add/remove tests ────────────────────────────────────────────────

class TestCompositeManagement:
    def test_add_child_increases_headcount(self) -> None:
        from organization.infrastructure.composite import EmployeeLeaf, CompositeOrgUnit

        unit_model = make_unit_model(1, "Dept", "department")
        composite = CompositeOrgUnit(unit_model, [])

        emp = make_employee_model(1, "Alice", "Dev", "5000")
        leaf = EmployeeLeaf(emp)
        composite.add_child(leaf)

        assert composite.get_headcount() == 1

    def test_remove_child_decreases_headcount(self) -> None:
        from organization.infrastructure.composite import EmployeeLeaf, CompositeOrgUnit

        emp = make_employee_model(1, "Alice", "Dev", "5000")
        leaf = EmployeeLeaf(emp)
        unit_model = make_unit_model(1, "Dept", "department")
        composite = CompositeOrgUnit(unit_model, [leaf])

        composite.remove_child(leaf)
        assert composite.get_headcount() == 0

    def test_get_children_returns_copy(self) -> None:
        from organization.infrastructure.composite import EmployeeLeaf, CompositeOrgUnit

        emp = make_employee_model(1, "Alice", "Dev", "5000")
        leaf = EmployeeLeaf(emp)
        unit_model = make_unit_model(1, "Dept", "department")
        composite = CompositeOrgUnit(unit_model, [leaf])

        children = composite.get_children()
        assert len(children) == 1
        # Modifying returned list should not affect composite
        children.clear()
        assert composite.get_headcount() == 1
