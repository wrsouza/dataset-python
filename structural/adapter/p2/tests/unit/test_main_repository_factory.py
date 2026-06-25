"""Unit tests for the _get_repository adapter-selection factory in main.py.

No autouse patching here (unlike tests/integration/test_api.py), so we can
exercise both branches of the factory directly.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import orm_adapter.main as main_module
from orm_adapter.infrastructure.raw_mysql_adapter import RawMySQLUserAdapter
from orm_adapter.infrastructure.sqlalchemy_adapter import SQLAlchemyUserAdapter


def test_get_repository_defaults_to_sqlalchemy() -> None:
    with main_module.app.test_request_context("/users"):
        repo = main_module._get_repository()

    assert isinstance(repo, SQLAlchemyUserAdapter)


def test_get_repository_raw_branch(monkeypatch) -> None:
    """Cover the ?adapter=raw branch — pymysql.connect is mocked, no real network."""
    fake_conn = MagicMock()
    monkeypatch.setattr(main_module.pymysql, "connect", lambda **_: fake_conn)

    with main_module.app.test_request_context("/users?adapter=raw"):
        repo = main_module._get_repository()

    assert isinstance(repo, RawMySQLUserAdapter)
    assert repo._conn is fake_conn
