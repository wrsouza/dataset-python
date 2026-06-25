"""Unit tests for PostgresTicketRepository using a fake DB-API connection."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from ticket_escalation.domain.entities import (
    EscalationStep,
    SupportTicket,
    SupportTier,
    TicketSeverity,
)
from ticket_escalation.infrastructure.postgres_repository import (
    PostgresTicketRepository,
)


class FakeCursor:
    def __init__(self, store: dict[str, tuple[Any, ...]]) -> None:
        self._store = store
        self._last_row: tuple[Any, ...] | None = None

    def execute(self, sql: str, params: tuple[Any, ...] = ()) -> None:
        statement = sql.strip()
        if statement.startswith("CREATE TABLE"):
            return
        if statement.startswith("INSERT"):
            self._store[params[0]] = params
        elif statement.startswith("SELECT"):
            self._last_row = self._store.get(params[0])

    def fetchone(self) -> tuple[Any, ...] | None:
        return self._last_row


class FakeConnection:
    def __init__(self) -> None:
        self._store: dict[str, tuple[Any, ...]] = {}

    def cursor(self) -> FakeCursor:
        return FakeCursor(self._store)

    def commit(self) -> None:
        pass


def _sample_ticket() -> SupportTicket:
    ticket = SupportTicket(
        ticket_id="t-42",
        subject="Billing issue",
        severity=TicketSeverity.MEDIUM,
        customer_email="c@example.com",
    )
    ticket.record_step(
        EscalationStep(
            tier=SupportTier.TIER_2,
            resolved=True,
            note="Refund issued",
            handled_at=datetime(2026, 1, 1, tzinfo=UTC),
        )
    )
    return ticket


def test_save_and_get_round_trips_ticket() -> None:
    repository = PostgresTicketRepository(FakeConnection())
    ticket = _sample_ticket()

    repository.save(ticket)
    fetched = repository.get(ticket.ticket_id)

    assert fetched is not None
    assert fetched.ticket_id == ticket.ticket_id
    assert fetched.resolved_by == SupportTier.TIER_2
    assert fetched.history[0].note == "Refund issued"


def test_get_returns_none_when_missing() -> None:
    repository = PostgresTicketRepository(FakeConnection())

    assert repository.get("unknown") is None


def test_save_unresolved_ticket_keeps_resolved_by_none() -> None:
    repository = PostgresTicketRepository(FakeConnection())
    ticket = SupportTicket(
        ticket_id="t-99",
        subject="Pending",
        severity=TicketSeverity.HIGH,
        customer_email="d@example.com",
    )

    repository.save(ticket)
    fetched = repository.get("t-99")

    assert fetched is not None
    assert fetched.resolved_by is None
    assert fetched.history == []
