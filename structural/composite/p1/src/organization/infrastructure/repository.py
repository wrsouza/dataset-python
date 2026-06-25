"""Repository: persistence operations for OrgUnit and Employee."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from organization.domain.entities import (
    EmployeeCreate,
    UnitCreate,
)
from organization.infrastructure.models import EmployeeModel, OrgUnitModel


class OrgUnitNotFoundError(Exception):
    def __init__(self, unit_id: int) -> None:
        super().__init__(f"OrgUnit {unit_id} not found")
        self.unit_id = unit_id


class OrgRepository:
    """Data-access layer for organizational hierarchy.

    SRP: only handles persistence — no business logic here.
    DIP: FastAPI routes and use cases depend on this class via injection.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def create_unit(self, data: UnitCreate, parent_id: int | None = None) -> OrgUnitModel:
        unit = OrgUnitModel(name=data.name, unit_type=data.unit_type, parent_id=parent_id)
        self._session.add(unit)
        self._session.flush()
        return unit

    def add_employee(self, unit_id: int, data: EmployeeCreate) -> EmployeeModel:
        unit = self.get_unit_or_raise(unit_id)
        employee = EmployeeModel(
            name=data.name,
            title=data.title,
            salary=data.salary,
            unit_id=unit.id,
        )
        self._session.add(employee)
        self._session.flush()
        return employee

    def get_unit_or_raise(self, unit_id: int) -> OrgUnitModel:
        unit = self._session.get(OrgUnitModel, unit_id)
        if unit is None:
            raise OrgUnitNotFoundError(unit_id)
        return unit

    def get_unit_with_tree(self, unit_id: int) -> OrgUnitModel:
        """Load unit with full eager-loaded subtree to avoid N+1."""
        stmt = (
            select(OrgUnitModel)
            .where(OrgUnitModel.id == unit_id)
            .options(
                selectinload(OrgUnitModel.children).selectinload(OrgUnitModel.children)
                .selectinload(OrgUnitModel.children)
                .selectinload(OrgUnitModel.employees),
                selectinload(OrgUnitModel.employees),
                selectinload(OrgUnitModel.children).selectinload(OrgUnitModel.employees),
                selectinload(OrgUnitModel.children)
                .selectinload(OrgUnitModel.children)
                .selectinload(OrgUnitModel.employees),
            )
        )
        result = self._session.execute(stmt).scalar_one_or_none()
        if result is None:
            raise OrgUnitNotFoundError(unit_id)
        return result

    def list_root_units(self) -> list[OrgUnitModel]:
        stmt = (
            select(OrgUnitModel)
            .where(OrgUnitModel.parent_id.is_(None))
            .options(
                selectinload(OrgUnitModel.children).selectinload(OrgUnitModel.children)
                .selectinload(OrgUnitModel.children)
                .selectinload(OrgUnitModel.employees),
                selectinload(OrgUnitModel.employees),
                selectinload(OrgUnitModel.children).selectinload(OrgUnitModel.employees),
                selectinload(OrgUnitModel.children)
                .selectinload(OrgUnitModel.children)
                .selectinload(OrgUnitModel.employees),
            )
        )
        return list(self._session.execute(stmt).scalars().all())

    def add_child_unit(self, parent_id: int, child_id: int) -> OrgUnitModel:
        parent = self.get_unit_or_raise(parent_id)
        child = self.get_unit_or_raise(child_id)
        child.parent_id = parent.id
        self._session.flush()
        return child
