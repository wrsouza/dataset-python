"""Unit tests for the submit/get ticket use cases."""

from __future__ import annotations

import pytest

from ticket_escalation.application.use_cases import (
    GetTicketUseCase,
    SubmitTicketUseCase,
    TicketNotFoundError,
)
from ticket_escalation.domain.entities import SupportTicket, SupportTier, TicketSeverity
from ticket_escalation.domain.interfaces import TicketRepository
from ticket_escalation.infrastructure.handlers import build_escalation_chain


class InMemoryTicketRepository(TicketRepository):
    """A dict-backed TicketRepository, used in place of PostgreSQL in tests."""

    def __init__(self) -> None:
        self._tickets: dict[str, SupportTicket] = {}

    def save(self, ticket: SupportTicket) -> None:
        self._tickets[ticket.ticket_id] = ticket

    def get(self, ticket_id: str) -> SupportTicket | None:
        return self._tickets.get(ticket_id)


def test_submit_ticket_persists_resolved_ticket() -> None:
    repository = InMemoryTicketRepository()
    use_case = SubmitTicketUseCase(build_escalation_chain(), repository)

    result = use_case.execute(
        subject="Password reset",
        severity=TicketSeverity.LOW,
        customer_email="a@example.com",
    )

    assert result.ticket.resolved_by == SupportTier.TIER_1
    assert repository.get(result.ticket.ticket_id) is not None


def test_get_ticket_returns_persisted_ticket() -> None:
    repository = InMemoryTicketRepository()
    submit = SubmitTicketUseCase(build_escalation_chain(), repository)
    get_ticket = GetTicketUseCase(repository)

    submitted = submit.execute(
        subject="Outage",
        severity=TicketSeverity.CRITICAL,
        customer_email="b@example.com",
    )

    fetched = get_ticket.execute(submitted.ticket.ticket_id)

    assert fetched.ticket_id == submitted.ticket.ticket_id


def test_get_ticket_raises_when_not_found() -> None:
    repository = InMemoryTicketRepository()
    get_ticket = GetTicketUseCase(repository)

    with pytest.raises(TicketNotFoundError):
        get_ticket.execute("missing-id")
