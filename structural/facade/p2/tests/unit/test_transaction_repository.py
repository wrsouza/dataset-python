from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from src.payment.domain.entities import Transaction
from src.payment.infrastructure.database import create_tables, init_engine
from src.payment.infrastructure.transaction_repository import (
    MySQLTransactionRepository,
)


@pytest.fixture
def session(tmp_path: Path) -> Session:
    database_url = f"sqlite:///{tmp_path}/repo_test.db"
    engine = init_engine(database_url)
    create_tables(database_url)
    return Session(bind=engine)


def test_save_and_find_by_id_roundtrip(session: Session) -> None:
    repository = MySQLTransactionRepository(session)
    transaction = Transaction.create("cus_1", 1500, "usd")

    repository.save(transaction)
    found = repository.find_by_id(transaction.id)

    assert found is not None
    assert found.id == transaction.id
    assert found.amount_cents == 1500
    assert found.status == transaction.status


def test_find_by_id_returns_none_when_missing(session: Session) -> None:
    repository = MySQLTransactionRepository(session)
    assert repository.find_by_id("missing-id") is None


def test_update_persists_new_status(session: Session) -> None:
    repository = MySQLTransactionRepository(session)
    transaction = Transaction.create("cus_1", 1500, "usd")
    repository.save(transaction)

    transaction.approve("ch_999")
    repository.update(transaction)

    found = repository.find_by_id(transaction.id)
    assert found is not None
    assert found.charge_id == "ch_999"
    assert found.status == transaction.status
