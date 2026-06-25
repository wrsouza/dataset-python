"""Shared pytest fixtures for the Support Ticket Escalation tests."""

from __future__ import annotations

import pytest
from flask.testing import FlaskClient

from ticket_escalation.app import create_app
from ticket_escalation.domain.entities import SupportTicket
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


@pytest.fixture
def repository() -> InMemoryTicketRepository:
    return InMemoryTicketRepository()


@pytest.fixture
def client(repository: InMemoryTicketRepository) -> FlaskClient:
    app = create_app(repository=repository, chain=build_escalation_chain())
    app.config.update(TESTING=True)
    return app.test_client()
