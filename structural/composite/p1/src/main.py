"""FastAPI application entry point for Organization Hierarchy API."""

from __future__ import annotations

from decimal import Decimal

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from organization.application.use_cases import OrgUnitUseCases
from organization.domain.entities import (
    AddChildRequest,
    EmployeeCreate,
    EmployeeResponse,
    HeadcountResponse,
    OrgUnitResponse,
    SalaryResponse,
    TreeNode,
    UnitCreate,
)
from organization.infrastructure.database import create_tables, get_session
from organization.infrastructure.repository import OrgRepository, OrgUnitNotFoundError

app = FastAPI(
    title="Organization Hierarchy API",
    description="Composite pattern demo: Company → Department → Team → Employee",
    version="0.1.0",
)


@app.on_event("startup")
def on_startup() -> None:
    create_tables()


def get_use_cases(session: Session = Depends(get_session)) -> OrgUnitUseCases:
    repo = OrgRepository(session)
    return OrgUnitUseCases(repo)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.post("/org/units", response_model=OrgUnitResponse, status_code=status.HTTP_201_CREATED)
def create_unit(
    data: UnitCreate,
    use_cases: OrgUnitUseCases = Depends(get_use_cases),
    session: Session = Depends(get_session),
) -> OrgUnitResponse:
    """Create a root-level org unit (Company, Department, or Team)."""
    result = use_cases.create_unit(data)
    session.commit()
    return result


@app.post(
    "/org/{parent_id}/children",
    response_model=OrgUnitResponse,
    status_code=status.HTTP_200_OK,
)
def add_child_unit(
    parent_id: int,
    request: AddChildRequest,
    use_cases: OrgUnitUseCases = Depends(get_use_cases),
    session: Session = Depends(get_session),
) -> OrgUnitResponse:
    """Attach an existing unit as a child of another unit."""
    try:
        result = use_cases.add_child_to_unit(parent_id, request)
        session.commit()
        return result
    except OrgUnitNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post(
    "/org/{unit_id}/employees",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_employee(
    unit_id: int,
    data: EmployeeCreate,
    use_cases: OrgUnitUseCases = Depends(get_use_cases),
    session: Session = Depends(get_session),
) -> EmployeeResponse:
    """Add an employee (leaf) to an org unit."""
    try:
        result = use_cases.add_employee_to_unit(unit_id, data)
        session.commit()
        return result
    except OrgUnitNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/org/{unit_id}/headcount", response_model=HeadcountResponse)
def get_headcount(
    unit_id: int,
    use_cases: OrgUnitUseCases = Depends(get_use_cases),
) -> HeadcountResponse:
    """Return headcount for a unit and all its descendants."""
    try:
        return use_cases.get_headcount(unit_id)
    except OrgUnitNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/org/{unit_id}/salary", response_model=SalaryResponse)
def get_total_salary(
    unit_id: int,
    use_cases: OrgUnitUseCases = Depends(get_use_cases),
) -> SalaryResponse:
    """Return total salary bill for a unit and all its descendants."""
    try:
        return use_cases.get_total_salary(unit_id)
    except OrgUnitNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/org/tree", response_model=list[TreeNode])
def get_org_tree(
    use_cases: OrgUnitUseCases = Depends(get_use_cases),
) -> list[TreeNode]:
    """Return the full organizational tree with recursive headcount/salary."""
    return use_cases.get_org_tree()
