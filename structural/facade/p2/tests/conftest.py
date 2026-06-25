"""Shared pytest fixtures for the Payment Processing Facade test suite."""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from flask.testing import FlaskClient

from src.payment.domain.entities import CreditCard, Customer

VALID_VISA_NUMBER = "4242424242424242"
DECLINED_VISA_NUMBER = "4000000000000002"


@pytest.fixture
def sqlite_database_url(tmp_path: Path) -> str:
    """SQLite file-based URL standing in for MySQL in tests.

    Decision: real MySQL is not guaranteed to be reachable when tests run
    outside docker-compose, so persistence tests exercise the same raw-SQL
    repository against SQLite. ``database.py`` deliberately avoids
    MySQL-only SQL (e.g. ``ON DUPLICATE KEY UPDATE``, ``AUTO_INCREMENT``)
    so the same schema and queries work identically on both engines.
    """
    return f"sqlite:///{tmp_path}/test.db"


@pytest.fixture
def valid_customer() -> Customer:
    return Customer(id="cus_1", name="Ada Lovelace", email="ada@example.com")


@pytest.fixture
def valid_card() -> CreditCard:
    return CreditCard(
        number=VALID_VISA_NUMBER,
        exp_month=12,
        exp_year=2099,
        cvc="123",
        holder_name="Ada Lovelace",
    )


@pytest.fixture
def declined_card() -> CreditCard:
    return CreditCard(
        number=DECLINED_VISA_NUMBER,
        exp_month=12,
        exp_year=2099,
        cvc="123",
        holder_name="Ada Lovelace",
    )


@pytest.fixture
def client(sqlite_database_url: str) -> Iterator[FlaskClient]:
    """FlaskClient wired against the real app, backed by SQLite.

    Decision: ``create_app()`` reads ``DATABASE_URL`` from the environment.
    Setting it to an in-memory-equivalent SQLite URL before importing
    ``src.payment.main`` redirects the same SQL schema/queries to SQLite.
    ``USE_MOCK_STRIPE`` keeps the real Stripe SDK out of the test run.
    """
    os.environ["DATABASE_URL"] = sqlite_database_url
    os.environ["USE_MOCK_STRIPE"] = "true"

    import importlib

    import src.payment.main as main_module

    importlib.reload(main_module)

    with main_module.app.test_client() as test_client:
        yield test_client

    os.environ.pop("DATABASE_URL", None)
    os.environ.pop("USE_MOCK_STRIPE", None)
