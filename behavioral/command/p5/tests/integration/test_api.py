"""Integration tests for the FastAPI account service, with fakes for I/O."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from event_sourcing.domain.entities import DomainEvent
from event_sourcing.domain.interfaces import EventPublisher, EventStore
from event_sourcing.main import app, get_event_store, get_publisher


class InMemoryEventStore(EventStore):
    def __init__(self) -> None:
        self._events: dict[str, list[DomainEvent]] = {}

    def append(self, event: DomainEvent) -> None:
        self._events.setdefault(event.account_id, []).append(event)

    def get_events(self, account_id: str) -> list[DomainEvent]:
        return list(self._events.get(account_id, []))


class FakeEventPublisher(EventPublisher):
    def __init__(self) -> None:
        self.published: list[DomainEvent] = []

    def publish(self, event: DomainEvent) -> None:
        self.published.append(event)


@pytest.fixture
def client() -> Iterator[TestClient]:
    store = InMemoryEventStore()
    publisher = FakeEventPublisher()
    app.dependency_overrides[get_event_store] = lambda: store
    app.dependency_overrides[get_publisher] = lambda: publisher
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_open_account_then_deposit_then_get_state(client: TestClient) -> None:
    client.post("/accounts/acc-1/open")
    client.post("/accounts/acc-1/deposit", json={"amount": 100.0})

    response = client.get("/accounts/acc-1")

    body = response.json()
    assert body["balance"] == 100.0
    assert body["is_open"] is True


def test_withdraw_more_than_balance_returns_400(client: TestClient) -> None:
    client.post("/accounts/acc-1/open")
    client.post("/accounts/acc-1/deposit", json={"amount": 10.0})

    response = client.post("/accounts/acc-1/withdraw", json={"amount": 50.0})

    assert response.status_code == 400


def test_deposit_without_opening_account_returns_400(client: TestClient) -> None:
    response = client.post("/accounts/acc-1/deposit", json={"amount": 10.0})

    assert response.status_code == 400


def test_opening_account_twice_returns_400(client: TestClient) -> None:
    client.post("/accounts/acc-1/open")

    response = client.post("/accounts/acc-1/open")

    assert response.status_code == 400


def test_event_history_lists_every_dispatched_command(client: TestClient) -> None:
    client.post("/accounts/acc-1/open")
    client.post("/accounts/acc-1/deposit", json={"amount": 20.0})
    client.post("/accounts/acc-1/withdraw", json={"amount": 5.0})

    response = client.get("/accounts/acc-1/events")

    event_types = [e["event_type"] for e in response.json()]
    assert event_types == ["account_opened", "funds_deposited", "funds_withdrawn"]
