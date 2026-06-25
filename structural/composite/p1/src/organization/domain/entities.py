"""Leaf and Composite dataclasses for the Organization Hierarchy."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ── Pydantic schemas (API layer) ──────────────────────────────────────────────

class EmployeeCreate(BaseModel):
    """Request schema for creating an employee."""

    name: str = Field(..., min_length=1, max_length=200)
    title: str = Field(..., min_length=1, max_length=200)
    salary: Decimal = Field(..., ge=Decimal("0"))


class UnitCreate(BaseModel):
    """Request schema for creating an org unit (Department, Team, Company)."""

    name: str = Field(..., min_length=1, max_length=200)
    unit_type: str = Field(..., pattern="^(company|department|team)$")


class AddChildRequest(BaseModel):
    """Request schema for adding a child unit to a parent."""

    child_id: int


class OrgUnitResponse(BaseModel):
    """Response schema for a single org unit."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    unit_type: str
    parent_id: int | None = None


class EmployeeResponse(BaseModel):
    """Response schema for a single employee."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    title: str
    salary: Decimal
    unit_id: int


class HeadcountResponse(BaseModel):
    unit_id: int
    headcount: int


class SalaryResponse(BaseModel):
    unit_id: int
    total_salary: Decimal


class TreeNode(BaseModel):
    """Recursive response for the full org tree."""

    id: int
    name: str
    unit_type: str
    headcount: int
    total_salary: Decimal
    children: list["TreeNode"] = Field(default_factory=list)
    members: list[MemberInfo] = Field(default_factory=list)


class MemberInfo(BaseModel):
    id: int
    name: str
    title: str
    salary: Decimal


TreeNode.model_rebuild()
