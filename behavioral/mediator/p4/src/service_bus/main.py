"""CLI entry point — Typer-based AWS SQS service bus mediator.

Composition root: the only place where the concrete SQS client is
built. All use cases receive abstractions (DIP).

Usage:
    python -m service_bus.main send billing-service '{"invoice_id": "i-1"}'
    python -m service_bus.main receive --max-messages 5
"""

from __future__ import annotations

import json

import typer

from service_bus.application.use_cases import (
    ReceiveMessagesUseCase,
    SendMessageUseCase,
)
from service_bus.infrastructure.factory import build_mediator

app = typer.Typer(
    name="service-bus",
    help="Mediator pattern demo: route messages between services via AWS SQS.",
    add_completion=False,
)


@app.command()
def send(sender_service: str, payload: str) -> None:
    """Send a JSON payload from `sender_service` onto the bus."""
    mediator = build_mediator()
    use_case = SendMessageUseCase(mediator)

    message = use_case.execute(sender_service, json.loads(payload))
    typer.echo(f"Sent message from '{message.sender_service}' at {message.sent_at}")


@app.command()
def receive(
    max_messages: int = typer.Option(10, "--max-messages", "-n"),
) -> None:
    """Pull up to `max_messages` pending messages off the bus."""
    mediator = build_mediator()
    use_case = ReceiveMessagesUseCase(mediator)

    messages = use_case.execute(max_messages)
    if not messages:
        typer.echo("No messages available.")
        return

    for message in messages:
        typer.echo(f"[{message.sender_service}] {message.payload} ({message.sent_at})")


if __name__ == "__main__":
    app()
