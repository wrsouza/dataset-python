"""Unit tests for SQLAlchemyUserAdapter.

Uses an in-memory SQLite database so no MySQL is needed.
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from orm_adapter.domain.entities import User, UserNotFoundError
from orm_adapter.infrastructure.sqlalchemy_adapter import (
    SQLAlchemyUserAdapter,
    _Base,
)


@pytest.fixture
def session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    _Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


@pytest.fixture
def adapter(session: Session) -> SQLAlchemyUserAdapter:
    return SQLAlchemyUserAdapter(session=session)


class TestSQLAlchemyUserAdapter:
    def test_save_inserts_new_user(self, adapter: SQLAlchemyUserAdapter) -> None:
        user = User(name="Alice", email="alice@example.com")
        saved = adapter.save(user)
        assert saved.id > 0
        assert saved.name == "Alice"

    def test_find_by_id_returns_user(self, adapter: SQLAlchemyUserAdapter) -> None:
        saved = adapter.save(User(name="Bob", email="bob@example.com"))
        found = adapter.find_by_id(saved.id)
        assert found is not None
        assert found.email == "bob@example.com"

    def test_find_by_id_returns_none_when_missing(
        self, adapter: SQLAlchemyUserAdapter
    ) -> None:
        assert adapter.find_by_id(9999) is None

    def test_find_all_returns_all_users(self, adapter: SQLAlchemyUserAdapter) -> None:
        adapter.save(User(name="C", email="c@example.com"))
        adapter.save(User(name="D", email="d@example.com"))
        users = adapter.find_all()
        assert len(users) >= 2

    def test_delete_removes_user(self, adapter: SQLAlchemyUserAdapter) -> None:
        saved = adapter.save(User(name="Eve", email="eve@example.com"))
        adapter.delete(saved.id)
        assert adapter.find_by_id(saved.id) is None

    def test_delete_raises_on_missing(self, adapter: SQLAlchemyUserAdapter) -> None:
        with pytest.raises(UserNotFoundError):
            adapter.delete(9999)
