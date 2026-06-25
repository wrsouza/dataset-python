"""SQLAlchemy 2.0 ORM models using adjacency list for hierarchy."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class OrgUnitModel(Base):
    """Represents any organizational unit (Company, Department, Team).

    Uses adjacency list: each row has an optional parent_id referencing
    another row in the same table.  The recursive CTE in the repository
    performs depth-first traversal without N+1 queries.
    """

    __tablename__ = "org_units"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    unit_type: Mapped[str] = mapped_column(String(50), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("org_units.id", ondelete="CASCADE"), nullable=True
    )

    parent: Mapped[OrgUnitModel | None] = relationship(
        "OrgUnitModel", back_populates="children", remote_side="OrgUnitModel.id"
    )
    children: Mapped[list[OrgUnitModel]] = relationship(
        "OrgUnitModel", back_populates="parent", cascade="all, delete-orphan"
    )
    employees: Mapped[list[EmployeeModel]] = relationship(
        "EmployeeModel", back_populates="unit", cascade="all, delete-orphan"
    )


class EmployeeModel(Base):
    """Leaf node: a single employee belonging to an OrgUnit."""

    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    salary: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    unit_id: Mapped[int] = mapped_column(
        ForeignKey("org_units.id", ondelete="CASCADE"), nullable=False
    )

    unit: Mapped[OrgUnitModel] = relationship("OrgUnitModel", back_populates="employees")
