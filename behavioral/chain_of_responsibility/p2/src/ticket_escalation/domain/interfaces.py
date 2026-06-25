"""Abstractions for the Chain of Responsibility escalation handlers."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ticket_escalation.domain.entities import SupportTicket


class TicketHandler(ABC):
    """A single link in the support ticket escalation chain.

    Each handler decides whether it can resolve a ticket. If it cannot,
    it forwards the ticket to the next handler in the chain, if any.
    """

    _next_handler: TicketHandler | None = None

    def set_next(self, handler: TicketHandler) -> TicketHandler:
        """Wire the next handler in the chain and return it for fluent chaining."""
        self._next_handler = handler
        return handler

    def handle(self, ticket: SupportTicket) -> SupportTicket:
        """Attempt to resolve the ticket, otherwise pass it along the chain."""
        if self._can_resolve(ticket):
            self._resolve(ticket)
            return ticket
        if self._next_handler is not None:
            return self._next_handler.handle(ticket)
        return ticket

    @abstractmethod
    def _can_resolve(self, ticket: SupportTicket) -> bool:
        """Decide whether this handler is able to resolve the ticket."""

    @abstractmethod
    def _resolve(self, ticket: SupportTicket) -> None:
        """Resolve the ticket and record the corresponding escalation step."""


class TicketRepository(ABC):
    """Persistence boundary for support tickets."""

    @abstractmethod
    def save(self, ticket: SupportTicket) -> None:
        """Persist the current state of a ticket."""

    @abstractmethod
    def get(self, ticket_id: str) -> SupportTicket | None:
        """Retrieve a ticket by its identifier, if it exists."""
