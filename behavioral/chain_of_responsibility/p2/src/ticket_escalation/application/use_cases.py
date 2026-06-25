"""Use cases orchestrating ticket creation and escalation through the chain."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from ticket_escalation.domain.entities import SupportTicket, TicketSeverity
from ticket_escalation.domain.interfaces import TicketHandler, TicketRepository


class TicketNotFoundError(Exception):
    """Raised when a ticket id has no matching record."""


@dataclass
class SubmitTicketResult:
    """Outcome returned to callers after submitting a ticket."""

    ticket: SupportTicket


class SubmitTicketUseCase:
    """Creates a ticket and routes it through the escalation chain."""

    def __init__(self, chain: TicketHandler, repository: TicketRepository) -> None:
        self._chain = chain
        self._repository = repository

    def execute(
        self, subject: str, severity: TicketSeverity, customer_email: str
    ) -> SubmitTicketResult:
        ticket = SupportTicket(
            ticket_id=str(uuid.uuid4()),
            subject=subject,
            severity=severity,
            customer_email=customer_email,
        )
        resolved_ticket = self._chain.handle(ticket)
        self._repository.save(resolved_ticket)
        return SubmitTicketResult(ticket=resolved_ticket)


class GetTicketUseCase:
    """Fetches a previously submitted ticket by id."""

    def __init__(self, repository: TicketRepository) -> None:
        self._repository = repository

    def execute(self, ticket_id: str) -> SupportTicket:
        ticket = self._repository.get(ticket_id)
        if ticket is None:
            raise TicketNotFoundError(f"Ticket {ticket_id} not found")
        return ticket
