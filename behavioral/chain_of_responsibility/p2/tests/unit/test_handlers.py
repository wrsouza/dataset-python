"""Unit tests for the escalation chain handlers."""

from __future__ import annotations

from ticket_escalation.domain.entities import SupportTicket, SupportTier, TicketSeverity
from ticket_escalation.infrastructure.handlers import build_escalation_chain


def _ticket(severity: TicketSeverity) -> SupportTicket:
    return SupportTicket(
        ticket_id="t-1",
        subject="Cannot log in",
        severity=severity,
        customer_email="user@example.com",
    )


def test_low_severity_resolved_at_tier_1() -> None:
    chain = build_escalation_chain()

    ticket = chain.handle(_ticket(TicketSeverity.LOW))

    assert ticket.is_resolved is True
    assert ticket.resolved_by == SupportTier.TIER_1
    assert len(ticket.history) == 1


def test_medium_severity_resolved_at_tier_2() -> None:
    chain = build_escalation_chain()

    ticket = chain.handle(_ticket(TicketSeverity.MEDIUM))

    assert ticket.resolved_by == SupportTier.TIER_2
    assert len(ticket.history) == 1


def test_high_severity_resolved_at_tier_3() -> None:
    chain = build_escalation_chain()

    ticket = chain.handle(_ticket(TicketSeverity.HIGH))

    assert ticket.resolved_by == SupportTier.TIER_3
    assert len(ticket.history) == 1


def test_critical_severity_escalates_to_management() -> None:
    chain = build_escalation_chain()

    ticket = chain.handle(_ticket(TicketSeverity.CRITICAL))

    assert ticket.resolved_by == SupportTier.MANAGEMENT
    assert len(ticket.history) == 1


def test_resolution_note_is_recorded() -> None:
    chain = build_escalation_chain()

    ticket = chain.handle(_ticket(TicketSeverity.LOW))

    assert ticket.history[0].note
    assert ticket.history[0].resolved is True


def test_handlers_chain_can_be_wired_individually() -> None:
    from ticket_escalation.infrastructure.handlers import (
        ManagementHandler,
        Tier1Handler,
        Tier2Handler,
        Tier3Handler,
    )

    tier1 = Tier1Handler()
    tier2 = Tier2Handler()
    tier3 = Tier3Handler()
    management = ManagementHandler()
    tier1.set_next(tier2)
    tier2.set_next(tier3)
    tier3.set_next(management)

    ticket = tier1.handle(_ticket(TicketSeverity.HIGH))

    assert ticket.resolved_by == SupportTier.TIER_3


def test_handler_without_next_returns_ticket_unresolved_if_it_cannot_resolve() -> None:
    from ticket_escalation.infrastructure.handlers import Tier1Handler

    tier1 = Tier1Handler()

    ticket = tier1.handle(_ticket(TicketSeverity.HIGH))

    assert ticket.is_resolved is False
    assert ticket.history == []
