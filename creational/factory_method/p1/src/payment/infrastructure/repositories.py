"""Concrete repository implementations backed by PostgreSQL via SQLAlchemy 2.0."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from payment.domain.entities import PaymentStatus, Transaction
from payment.infrastructure.database import TransactionORM


class PostgresTransactionRepository:
    """ConcreteRepository — persists transactions to PostgreSQL.

    The use case depends only on the TransactionRepository Protocol (DIP),
    so this class can be swapped without touching application logic.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, transaction: Transaction) -> None:
        orm = TransactionORM(
            id=transaction.id,
            gateway=transaction.gateway,
            amount=transaction.amount,
            currency=transaction.currency,
            status=transaction.status.value,
            created_at=transaction.created_at,
            gateway_reference=transaction.gateway_reference,
            error_message=transaction.error_message,
        )
        self._session.merge(orm)
        self._session.commit()

    def find_by_id(self, transaction_id: str) -> Transaction | None:
        orm = self._session.get(TransactionORM, transaction_id)
        if orm is None:
            return None
        return self._to_entity(orm)

    def list_all(self) -> list[Transaction]:
        rows = self._session.query(TransactionORM).order_by(
            TransactionORM.created_at.desc()
        ).all()
        return [self._to_entity(row) for row in rows]

    @staticmethod
    def _to_entity(orm: TransactionORM) -> Transaction:
        return Transaction(
            id=orm.id,
            gateway=orm.gateway,
            amount=float(orm.amount),
            currency=orm.currency,
            status=PaymentStatus(orm.status),
            created_at=orm.created_at,
            gateway_reference=orm.gateway_reference,
            error_message=orm.error_message,
        )
