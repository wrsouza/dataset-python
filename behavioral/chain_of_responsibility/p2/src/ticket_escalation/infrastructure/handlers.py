"""Concrete escalation handlers ordered Tier 1 -> Tier 2 -> Tier 3 -> Management."""

from __future__ import annotations

from datetime import UTC, datetime

from ticket_escalation.domain.entities import (
    EscalationStep,
    SupportTicket,
    SupportTier,
    TicketSeverity,
)
from ticket_escalation.domain.interfaces import TicketHandler


class Tier1Handler(TicketHandler):
    """Front-line support: resolves low severity tickets only."""

    def _can_resolve(self, ticket: SupportTicket) -> bool:
        return ticket.severity == TicketSeverity.LOW

    def _resolve(self, ticket: SupportTicket) -> None:
        ticket.record_step(
            EscalationStep(
                tier=SupportTier.TIER_1,
                resolved=True,
                note="Resolved with a standard troubleshooting script.",
                handled_at=datetime.now(UTC),
            )
        )


class Tier2Handler(TicketHandler):
    """Specialist support: resolves low and medium severity tickets."""

    def _can_resolve(self, ticket: SupportTicket) -> bool:
        return ticket.severity in (TicketSeverity.LOW, TicketSeverity.MEDIUM)

    def _resolve(self, ticket: SupportTicket) -> None:
        ticket.record_step(
            EscalationStep(
                tier=SupportTier.TIER_2,
                resolved=True,
                note="Resolved after specialist diagnosis.",
                handled_at=datetime.now(UTC),
            )
        )


class Tier3Handler(TicketHandler):
    """Engineering support: resolves anything up to high severity."""

    def _can_resolve(self, ticket: SupportTicket) -> bool:
        return ticket.severity in (
            TicketSeverity.LOW,
            TicketSeverity.MEDIUM,
            TicketSeverity.HIGH,
        )

    def _resolve(self, ticket: SupportTicket) -> None:
        ticket.record_step(
            EscalationStep(
                tier=SupportTier.TIER_3,
                resolved=True,
                note="Resolved by engineering after root-cause analysis.",
                handled_at=datetime.now(UTC),
            )
        )


class ManagementHandler(TicketHandler):
    """Final link: handles critical tickets that nobody else could resolve."""

    def _can_resolve(self, ticket: SupportTicket) -> bool:
        return True

    def _resolve(self, ticket: SupportTicket) -> None:
        ticket.record_step(
            EscalationStep(
                tier=SupportTier.MANAGEMENT,
                resolved=True,
                note="Resolved at management level with customer follow-up.",
                handled_at=datetime.now(UTC),
            )
        )


def build_escalation_chain() -> TicketHandler:
    """Wire the default Tier 1 -> Tier 2 -> Tier 3 -> Management chain."""
    tier1 = Tier1Handler()
    tier2 = Tier2Handler()
    tier3 = Tier3Handler()
    management = ManagementHandler()
    tier1.set_next(tier2).set_next(tier3).set_next(management)
    return tier1
