"""Use cases orchestrate the Composite pattern operations."""

from __future__ import annotations

from decimal import Decimal

from organization.domain.entities import (
    AddChildRequest,
    EmployeeCreate,
    EmployeeResponse,
    HeadcountResponse,
    MemberInfo,
    OrgUnitResponse,
    SalaryResponse,
    TreeNode,
    UnitCreate,
)
from organization.infrastructure.composite import build_composite_tree
from organization.infrastructure.repository import OrgRepository


class OrgUnitUseCases:
    """All business operations for the org hierarchy.

    DIP: depends on OrgRepository abstraction injected via constructor.
    SRP: orchestration only — no SQL, no HTTP concerns.
    """

    def __init__(self, repository: OrgRepository) -> None:
        self._repo = repository

    def create_unit(self, data: UnitCreate, parent_id: int | None = None) -> OrgUnitResponse:
        unit = self._repo.create_unit(data, parent_id)
        return OrgUnitResponse.model_validate(unit)

    def add_employee_to_unit(self, unit_id: int, data: EmployeeCreate) -> EmployeeResponse:
        employee = self._repo.add_employee(unit_id, data)
        return EmployeeResponse.model_validate(employee)

    def add_child_to_unit(self, parent_id: int, request: AddChildRequest) -> OrgUnitResponse:
        child = self._repo.add_child_unit(parent_id, request.child_id)
        return OrgUnitResponse.model_validate(child)

    def get_headcount(self, unit_id: int) -> HeadcountResponse:
        unit_model = self._repo.get_unit_with_tree(unit_id)
        # Build composite tree and call uniform interface — no isinstance needed
        composite = build_composite_tree(unit_model)
        return HeadcountResponse(unit_id=unit_id, headcount=composite.get_headcount())

    def get_total_salary(self, unit_id: int) -> SalaryResponse:
        unit_model = self._repo.get_unit_with_tree(unit_id)
        composite = build_composite_tree(unit_model)
        return SalaryResponse(unit_id=unit_id, total_salary=composite.get_total_salary())

    def get_org_tree(self) -> list[TreeNode]:
        roots = self._repo.list_root_units()
        return [self._build_tree_node(root_model) for root_model in roots]

    def _build_tree_node(self, unit_model: object) -> TreeNode:
        """Recursively converts the ORM tree to the API response tree."""
        from organization.infrastructure.models import OrgUnitModel  # noqa: PLC0415

        assert isinstance(unit_model, OrgUnitModel)  # noqa: S101

        composite = build_composite_tree(unit_model)

        members = [
            MemberInfo(
                id=0,  # ID not needed in display; use employee sub-route for details
                name=m.name,
                title=m.title,
                salary=m.salary,
            )
            for m in unit_model.employees
        ]

        children_nodes = [self._build_tree_node(child) for child in unit_model.children]

        return TreeNode(
            id=unit_model.id,
            name=unit_model.name,
            unit_type=unit_model.unit_type,
            headcount=composite.get_headcount(),
            total_salary=composite.get_total_salary(),
            children=children_nodes,
            members=members,
        )
