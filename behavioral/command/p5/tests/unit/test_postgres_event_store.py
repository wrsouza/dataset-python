"""Unit tests for PostgresEventStore using a fake DB-API connection."""

from __future__ import annotations

from typing import Any

from event_sourcing.domain.entities import DomainEvent, EventType
from event_sourcing.infrastructure.postgres_event_store import PostgresEventStore


class FakeCursor:
    def __init__(self, rows: list[tuple[Any, ...]]) -> None:
        self._rows = rows
        self._result: list[tuple[Any, ...]] = []

    def execute(self, sql: str, params: tuple[Any, ...] = ()) -> None:
        statement = sql.strip()
        if statement.startswith("CREATE TABLE"):
            return
        if statement.startswith("INSERT"):
            self._rows.append(params)
        elif statement.startswith("SELECT"):
            account_id = params[0]
            self._result = [row for row in self._rows if row[1] == account_id]

    def fetchall(self) -> list[tuple[Any, ...]]:
        return self._result


class FakeConnection:
    def __init__(self) -> None:
        self._rows: list[tuple[Any, ...]] = []

    def cursor(self) -> FakeCursor:
        return FakeCursor(self._rows)

    def commit(self) -> None:
        pass


def test_append_and_get_events_round_trips() -> None:
    store = PostgresEventStore(FakeConnection())
    event = DomainEvent.new("acc-1", EventType.ACCOUNT_OPENED, {})

    store.append(event)
    fetched = store.get_events("acc-1")

    assert len(fetched) == 1
    assert fetched[0].event_id == event.event_id
    assert fetched[0].event_type == EventType.ACCOUNT_OPENED


def test_get_events_returns_empty_list_for_unknown_account() -> None:
    store = PostgresEventStore(FakeConnection())

    assert store.get_events("unknown") == []


def test_get_events_filters_by_account_id() -> None:
    store = PostgresEventStore(FakeConnection())
    store.append(DomainEvent.new("acc-1", EventType.ACCOUNT_OPENED, {}))
    store.append(DomainEvent.new("acc-2", EventType.ACCOUNT_OPENED, {}))

    fetched = store.get_events("acc-1")

    assert len(fetched) == 1
    assert fetched[0].account_id == "acc-1"


def test_get_events_preserves_payload() -> None:
    store = PostgresEventStore(FakeConnection())
    store.append(DomainEvent.new("acc-1", EventType.FUNDS_DEPOSITED, {"amount": 42.5}))

    [fetched] = store.get_events("acc-1")

    assert fetched.payload == {"amount": 42.5}
