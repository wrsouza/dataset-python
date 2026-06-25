"""Flask application factory for the Support Ticket Escalation API.

Composition root: the only place that wires the concrete PostgreSQL
connection and the escalation chain into the use cases.
"""

from __future__ import annotations

from flask import Flask, jsonify, request
from flask.wrappers import Response

from ticket_escalation.application.use_cases import (
    GetTicketUseCase,
    SubmitTicketUseCase,
    TicketNotFoundError,
)
from ticket_escalation.domain.entities import SupportTicket, TicketSeverity
from ticket_escalation.domain.interfaces import TicketHandler, TicketRepository
from ticket_escalation.infrastructure.factory import build_connection, build_repository
from ticket_escalation.infrastructure.handlers import build_escalation_chain


def _ticket_to_dict(ticket: SupportTicket) -> dict[str, object]:
    return {
        "ticket_id": ticket.ticket_id,
        "subject": ticket.subject,
        "severity": ticket.severity.value,
        "customer_email": ticket.customer_email,
        "is_resolved": ticket.is_resolved,
        "resolved_by": ticket.resolved_by.value if ticket.resolved_by else None,
        "history": [
            {
                "tier": step.tier.value,
                "resolved": step.resolved,
                "note": step.note,
                "handled_at": step.handled_at.isoformat(),
            }
            for step in ticket.history
        ],
    }


def create_app(
    repository: TicketRepository | None = None,
    chain: TicketHandler | None = None,
) -> Flask:
    """Build and configure the Flask app.

    `repository` and `chain` can be injected (e.g. an in-memory fake
    repository in tests) so integration tests never need a real database.
    """
    app = Flask(__name__)

    ticket_repository = repository or build_repository(build_connection())
    escalation_chain = chain or build_escalation_chain()

    submit_ticket = SubmitTicketUseCase(escalation_chain, ticket_repository)
    get_ticket = GetTicketUseCase(ticket_repository)

    @app.post("/tickets")
    def submit_ticket_route() -> tuple[Response, int]:
        payload = request.get_json(force=True)
        result = submit_ticket.execute(
            subject=payload["subject"],
            severity=TicketSeverity(payload["severity"]),
            customer_email=payload["customer_email"],
        )
        return jsonify(_ticket_to_dict(result.ticket)), 201

    @app.get("/tickets/<ticket_id>")
    def get_ticket_route(ticket_id: str) -> tuple[Response, int] | Response:
        try:
            ticket = get_ticket.execute(ticket_id)
        except TicketNotFoundError as exc:
            return jsonify({"error": str(exc)}), 404
        return jsonify(_ticket_to_dict(ticket))

    @app.get("/health")
    def health() -> Response:
        return jsonify({"status": "ok"})

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=False)
