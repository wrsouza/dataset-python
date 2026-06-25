"""Integration tests for the FastAPI application using TestClient.

Decision: PostgreSQL is not available in this execution environment, so these
tests override the `get_db` dependency with an in-memory SQLite session. The
ORM models, repositories, and routes are exercised exactly as in production;
only the database engine differs. This keeps the suite runnable with plain
`pytest` while `docker-compose run --rm app pytest` still exercises the real
PostgreSQL service end-to-end.
"""

from __future__ import annotations

import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Point at an in-memory SQLite database *before* importing `main`, because
# importing it triggers `Base.metadata.create_all(bind=engine)` at module
# level. Without this, the import would attempt a real PostgreSQL connection.
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    import main as main_module
    from tax.infrastructure.database.models import Base

    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    test_session_local = sessionmaker(bind=test_engine, expire_on_commit=False)
    Base.metadata.create_all(bind=test_engine)

    def _override_get_db() -> Generator[Session, None, None]:
        db = test_session_local()
        try:
            yield db
        finally:
            db.close()

    main_module.app.dependency_overrides[main_module.get_db] = _override_get_db

    with TestClient(main_module.app) as test_client:
        yield test_client

    main_module.app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def seeded_customer_id(client: TestClient) -> str:
    """Insert a Brazilian customer directly via the repository for use in tests."""
    import main as main_module
    from tax.domain.entities import Customer, CustomerCountry
    from tax.infrastructure.database.repository import CustomerRepository

    override = next(iter(main_module.app.dependency_overrides.values()))
    db = next(override())
    try:
        customer = Customer(
            id="customer-1",
            name="Maria Silva",
            country=CustomerCountry.BRAZIL,
            tax_id="123.456.789-00",
        )
        CustomerRepository(db).save(customer)
        return customer.id
    finally:
        db.close()


def test_list_strategies_returns_all_registered_strategies(client: TestClient) -> None:
    response = client.get("/tax/strategies")

    assert response.status_code == 200
    names = {item["name"] for item in response.json()}
    assert names == {"brazil", "us", "eu", "exempt"}


def test_create_order_persists_and_returns_id(client: TestClient) -> None:
    payload = {
        "customer_id": "customer-1",
        "order_type": "B2C",
        "items": [
            {
                "product_id": "sku-1",
                "description": "Keyboard",
                "quantity": 1,
                "unit_price": "100.00",
            }
        ],
    }

    response = client.post("/orders", json=payload)

    assert response.status_code == 201
    assert response.json()["status"] == "created"


def test_calculate_tax_for_brazilian_order_applies_expected_taxes(
    client: TestClient, seeded_customer_id: str
) -> None:
    order_payload = {
        "customer_id": seeded_customer_id,
        "order_type": "B2C",
        "items": [
            {
                "product_id": "sku-1",
                "description": "Keyboard",
                "quantity": 1,
                "unit_price": "100.00",
            }
        ],
    }
    create_response = client.post("/orders", json=order_payload)
    order_id = create_response.json()["id"]

    response = client.post(f"/orders/{order_id}/calculate-tax?strategy=brazil")

    assert response.status_code == 200
    body = response.json()
    assert body["subtotal"] == "100.0000"
    tax_names = {line["name"] for line in body["taxes"]}
    assert tax_names == {"ICMS", "PIS", "COFINS"}
    assert body["strategy_used"] == "brazil"


def test_calculate_tax_for_unknown_order_returns_404(client: TestClient) -> None:
    response = client.post("/orders/does-not-exist/calculate-tax?strategy=brazil")

    assert response.status_code == 404


def test_calculate_tax_with_invalid_strategy_returns_400(
    client: TestClient, seeded_customer_id: str
) -> None:
    order_payload = {
        "customer_id": seeded_customer_id,
        "order_type": "B2C",
        "items": [
            {
                "product_id": "sku-1",
                "description": "Keyboard",
                "quantity": 1,
                "unit_price": "10.00",
            }
        ],
    }
    create_response = client.post("/orders", json=order_payload)
    order_id = create_response.json()["id"]

    response = client.post(f"/orders/{order_id}/calculate-tax?strategy=mars")

    assert response.status_code == 400
