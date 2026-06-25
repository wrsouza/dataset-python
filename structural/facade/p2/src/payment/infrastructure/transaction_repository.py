from __future__ import annotations

import logging
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.payment.domain.entities import Transaction, TransactionId, TransactionStatus

logger = logging.getLogger(__name__)


class MySQLTransactionRepository:
    """Persists and retrieves payment transactions in MySQL.

    SQL is kept portable (no MySQL-only syntax such as ``ON DUPLICATE KEY``)
    so the same statements run unmodified against SQLite in tests.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, transaction: Transaction) -> None:
        self._session.execute(
            text(
                "INSERT INTO transactions "
                "(id, customer_id, amount_cents, currency, status, "
                "charge_id, failure_reason, created_at, updated_at) "
                "VALUES "
                "(:id, :cid, :amount, :currency, :status, "
                ":charge, :reason, :cat, :uat)"
            ),
            {
                "id": transaction.id,
                "cid": transaction.customer_id,
                "amount": transaction.amount_cents,
                "currency": transaction.currency,
                "status": transaction.status.value,
                "charge": transaction.charge_id,
                "reason": transaction.failure_reason,
                "cat": transaction.created_at,
                "uat": transaction.updated_at,
            },
        )
        self._session.commit()
        logger.info("Transaction %s saved", transaction.id)

    def find_by_id(self, transaction_id: TransactionId) -> Transaction | None:
        row = self._session.execute(
            text(
                "SELECT id, customer_id, amount_cents, currency, status, "
                "charge_id, failure_reason, created_at, updated_at "
                "FROM transactions WHERE id = :id"
            ),
            {"id": transaction_id},
        ).fetchone()

        if row is None:
            return None

        return Transaction(
            id=row[0],
            customer_id=row[1],
            amount_cents=row[2],
            currency=row[3],
            status=TransactionStatus(row[4]),
            charge_id=row[5],
            failure_reason=row[6],
            created_at=row[7],
            updated_at=row[8],
        )

    def update(self, transaction: Transaction) -> None:
        transaction.updated_at = datetime.utcnow()
        self._session.execute(
            text(
                "UPDATE transactions SET status = :status, charge_id = :charge, "
                "failure_reason = :reason, updated_at = :uat WHERE id = :id"
            ),
            {
                "status": transaction.status.value,
                "charge": transaction.charge_id,
                "reason": transaction.failure_reason,
                "uat": transaction.updated_at,
                "id": transaction.id,
            },
        )
        self._session.commit()
        logger.info("Transaction %s updated to %s", transaction.id, transaction.status)
