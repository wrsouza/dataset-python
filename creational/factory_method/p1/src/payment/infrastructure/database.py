"""SQLAlchemy 2.0 database setup and ORM models for the payment domain."""
from __future__ import annotations

import os
from datetime import datetime

from sqlalchemy import DateTime, Enum, Numeric, String, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from payment.domain.entities import PaymentStatus

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://app:secret@db:5432/paymentdb",
)


class Base(DeclarativeBase):
    pass


class TransactionORM(Base):
    """ORM mapping for the transactions table."""

    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    gateway: Mapped[str] = mapped_column(String(32), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(PaymentStatus, name="payment_status"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False
    )
    gateway_reference: Mapped[str | None] = mapped_column(String(128), nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(512), nullable=True)


def create_db_engine() -> "sqlalchemy.engine.Engine":  # type: ignore[name-defined]
    from sqlalchemy import create_engine as _create

    return _create(DATABASE_URL, pool_pre_ping=True)


def init_db(engine: "sqlalchemy.engine.Engine") -> None:  # type: ignore[name-defined]
    """Create all tables. Safe to call multiple times."""
    Base.metadata.create_all(engine)
