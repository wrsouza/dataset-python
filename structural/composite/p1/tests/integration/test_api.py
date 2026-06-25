"""Integration tests for the Organization Hierarchy API."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app, get_use_cases
from organization.application.use_cases import OrgUnitUseCases
from organization.infrastructure.database import get_session
from organization.infrastructure.models import Base
from organization.infrastructure.repository import OrgRepository

DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(autouse=True)
def setup_db() -> None:
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client() -> TestClient:
    def override_session():  # type: ignore[return]
        with TestingSession() as session:
            yield session

    def override_use_cases(session=None):  # type: ignore[return, assignment]
        with TestingSession() as s:
            repo = OrgRepository(s)
            yield OrgUnitUseCases(repo)

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_use_cases] = override_use_cases
    return TestClient(app)


@pytest.fixture()
def seeded_client(client: TestClient) -> tuple[TestClient, dict]:
    """Return client plus IDs for a pre-seeded company/dept/team/employees."""
    # Create company
    company = client.post(
        "/org/units", json={"name": "Acme Corp", "unit_type": "company"}
    ).json()

    # Create department
    dept = client.post(
        "/org/units", json={"name": "Engineering", "unit_type": "department"}
    ).json()

    # Create team
    team = client.post(
        "/org/units", json={"name": "Backend", "unit_type": "team"}
    ).json()

    # Wire hierarchy
    client.post(f"/org/{company['id']}/children", json={"child_id": dept["id"]})
    client.post(f"/org/{dept['id']}/children", json={"child_id": team["id"]})

    # Add employees
    client.post(
        f"/org/{team['id']}/employees",
        json={"name": "Alice", "title": "Senior Dev", "salary": "10000"},
    )
    client.post(
        f"/org/{team['id']}/employees",
        json={"name": "Bob", "title": "Junior Dev", "salary": "6000"},
    )
    client.post(
        f"/org/{dept['id']}/employees",
        json={"name": "Carol", "title": "VP Eng", "salary": "20000"},
    )

    return client, {
        "company_id": company["id"],
        "dept_id": dept["id"],
        "team_id": team["id"],
    }


class TestOrgUnitCreation:
    def test_create_company_returns_201(self, client: TestClient) -> None:
        resp = client.post(
            "/org/units", json={"name": "TestCorp", "unit_type": "company"}
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "TestCorp"
        assert data["unit_type"] == "company"

    def test_invalid_unit_type_rejected(self, client: TestClient) -> None:
        resp = client.post(
            "/org/units", json={"name": "X", "unit_type": "invalid"}
        )
        assert resp.status_code == 422


class TestHeadcount:
    def test_team_headcount(self, seeded_client: tuple) -> None:
        client, ids = seeded_client
        resp = client.get(f"/org/{ids['team_id']}/headcount")
        assert resp.status_code == 200
        assert resp.json()["headcount"] == 2  # Alice + Bob

    def test_dept_headcount_includes_team(self, seeded_client: tuple) -> None:
        client, ids = seeded_client
        resp = client.get(f"/org/{ids['dept_id']}/headcount")
        assert resp.json()["headcount"] == 3  # Carol + Alice + Bob

    def test_company_headcount_is_all(self, seeded_client: tuple) -> None:
        client, ids = seeded_client
        resp = client.get(f"/org/{ids['company_id']}/headcount")
        assert resp.json()["headcount"] == 3

    def test_headcount_not_found(self, client: TestClient) -> None:
        resp = client.get("/org/9999/headcount")
        assert resp.status_code == 404


class TestSalary:
    def test_team_salary(self, seeded_client: tuple) -> None:
        client, ids = seeded_client
        resp = client.get(f"/org/{ids['team_id']}/salary")
        assert resp.status_code == 200
        assert float(resp.json()["total_salary"]) == 16000.0

    def test_dept_salary(self, seeded_client: tuple) -> None:
        client, ids = seeded_client
        resp = client.get(f"/org/{ids['dept_id']}/salary")
        assert float(resp.json()["total_salary"]) == 36000.0

    def test_company_salary(self, seeded_client: tuple) -> None:
        client, ids = seeded_client
        resp = client.get(f"/org/{ids['company_id']}/salary")
        assert float(resp.json()["total_salary"]) == 36000.0


class TestOrgTree:
    def test_tree_has_nested_children(self, seeded_client: tuple) -> None:
        client, ids = seeded_client
        resp = client.get("/org/tree")
        assert resp.status_code == 200
        tree = resp.json()
        assert len(tree) >= 1
        company = tree[0]
        assert company["name"] == "Acme Corp"
        assert company["headcount"] == 3
        assert len(company["children"]) >= 1
