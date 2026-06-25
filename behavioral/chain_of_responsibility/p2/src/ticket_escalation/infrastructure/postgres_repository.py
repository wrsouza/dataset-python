"""PostgreSQL-backed implementation of TicketRepository."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Protocol

from ticket_escalation.domain.entities import (
    EscalationStep,
    SupportTicket,
    SupportTier,
    TicketSeverity,
)
from ticket_escalation.domain.interfaces import TicketRepository

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS support_tickets (
    ticket_id TEXT PRIMARY KEY,
    subject TEXT NOT NULL,
    severity TEXT NOT NULL,
    customer_email TEXT NOT NULL,
    is_resolved BOOLEAN NOT NULL,
    resolved_by TEXT,
    history JSONB NOT NULL
)
"""

UPSERT_SQL = """
INSERT INTO support_tickets
    (ticket_id, subject, severity, customer_email, is_resolved, resolved_by, history)
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (ticket_id) DO UPDATE SET
    subject = EXCLUDED.subject,
    severity = EXCLUDED.severity,
    customer_email = EXCLUDED.customer_email,
    is_resolved = EXCLUDED.is_resolved,
    resolved_by = EXCLUDED.resolved_by,
    history = EXCLUDED.history
"""

SELECT_SQL = """
SELECT ticket_id, subject, severity, customer_email, is_resolved, resolved_by, history
FROM support_tickets
WHERE ticket_id = %s
"""


class DBConnection(Protocol):
    """Minimal DB-API connection contract this repository relies on."""

    def cursor(self) -> Any: ...

    def commit(self) -> None: ...


def _serialize_history(history: list[EscalationStep]) -> str:
    return json.dumps(
        [
            {
                "tier": step.tier.value,
                "resolved": step.resolved,
                "note": step.note,
                "handled_at": step.handled_at.isoformat(),
            }
            for step in history
        ]
    )


def _deserialize_history(raw: str | list[dict[str, Any]]) -> list[EscalationStep]:
    items = json.loads(raw) if isinstance(raw, str) else raw
    return [
        EscalationStep(
            tier=SupportTier(item["tier"]),
            resolved=item["resolved"],
            note=item["note"],
            handled_at=datetime.fromisoformat(item["handled_at"]),
        )
        for item in items
    ]


class PostgresTicketRepository(TicketRepository):
    """Stores support tickets in a PostgreSQL `support_tickets` table."""

    def __init__(self, connection: DBConnection) -> None:
        self._connection = connection
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        cursor = self._connection.cursor()
        cursor.execute(CREATE_TABLE_SQL)
        self._connection.commit()

    def save(self, ticket: SupportTicket) -> None:
        cursor = self._connection.cursor()
        cursor.execute(
            UPSERT_SQL,
            (
                ticket.ticket_id,
                ticket.subject,
                ticket.severity.value,
                ticket.customer_email,
                ticket.is_resolved,
                ticket.resolved_by.value if ticket.resolved_by else None,
                _serialize_history(ticket.history),
            ),
        )
        self._connection.commit()

    def get(self, ticket_id: str) -> SupportTicket | None:
        cursor = self._connection.cursor()
        cursor.execute(SELECT_SQL, (ticket_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        (
            db_ticket_id,
            subject,
            severity,
            customer_email,
            is_resolved,
            resolved_by,
            history,
        ) = row
        return SupportTicket(
            ticket_id=db_ticket_id,
            subject=subject,
            severity=TicketSeverity(severity),
            customer_email=customer_email,
            is_resolved=is_resolved,
            resolved_by=SupportTier(resolved_by) if resolved_by else None,
            history=_deserialize_history(history),
        )
