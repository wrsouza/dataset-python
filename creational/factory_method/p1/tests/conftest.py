"""Shared test fixtures for P1 — Payment Gateway Factory."""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from payment.domain.entities import PaymentRequest
from payment.infrastructure.database import Base


@pytest.fixture(scope="session")
def in_memory_engine():
    """SQLite in-memory engine for fast unit/integration tests."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(in_memory_engine):
    """Transactional session that rolls back after each test."""
    with Session(in_memory_engine) as session:
        yield session


@pytest.fixture
def sample_request() -> PaymentRequest:
    return PaymentRequest(amount=99.99, currency="USD", metadata={"order_id": "ORD-001"})
