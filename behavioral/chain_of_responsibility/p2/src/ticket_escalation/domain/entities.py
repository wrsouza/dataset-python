"""Core entities for the support ticket escalation domain."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class TicketSeverity(StrEnum):
    """Severity levels a support ticket can be raised with."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SupportTier(StrEnum):
    """Support tiers a ticket can be escalated through."""

    TIER_1 = "tier_1"
    TIER_2 = "tier_2"
    TIER_3 = "tier_3"
    MANAGEMENT = "management"


@dataclass
class EscalationStep:
    """A single hop the ticket made through the handler chain."""

    tier: SupportTier
    resolved: bool
    note: str
    handled_at: datetime


@dataclass
class SupportTicket:
    """A customer support ticket moving through the escalation chain."""

    ticket_id: str
    subject: str
    severity: TicketSeverity
    customer_email: str
    is_resolved: bool = False
    resolved_by: SupportTier | None = None
    history: list[EscalationStep] = field(default_factory=list)

    def record_step(self, step: EscalationStep) -> None:
        """Append a handling step and mark the ticket resolved if applicable."""
        self.history.append(step)
        if step.resolved:
            self.is_resolved = True
            self.resolved_by = step.tier
