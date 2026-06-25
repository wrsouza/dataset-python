"""CLI entry point — Typer-based message processing pipeline.

Composition root: the only place where the concrete RabbitMQ channel is
built. All use cases receive abstractions (DIP).

Usage:
    python -m message_pipeline.main process --queue orders --limit 10
    python -m message_pipeline.main simulate --message-id m-1 \\
        --payload '{"order_id": "o-1", "amount": 42}'
"""

from __future__ import annotations

import json
from typing import Annotated

import typer

from message_pipeline.application.use_cases import (
    ConsumeAndProcessUseCase,
    ProcessMessageUseCase,
)
from message_pipeline.domain.entities import IncomingMessage
from message_pipeline.infrastructure.factory import build_consumer
from message_pipeline.infrastructure.handlers import build_processing_chain

app = typer.Typer(
    name="message-pipeline",
    help="Chain of Responsibility demo: validate, deduplicate, and route messages.",
    add_completion=False,
)


def _print_message(message: IncomingMessage) -> None:
    last_step = message.history[-1] if message.history else None
    color = (
        typer.colors.GREEN if message.status.value == "processed" else typer.colors.RED
    )
    typer.echo(
        f"  [{message.message_id}] "
        + typer.style(message.status.value, fg=color, bold=True)
        + (f" — {last_step.reason}" if last_step else "")
    )


@app.command()
def process(
    queue: Annotated[str, typer.Option("--queue", "-q", help="RabbitMQ queue name")],
    limit: Annotated[
        int, typer.Option("--limit", "-l", help="Max messages to consume")
    ] = 10,
) -> None:
    """Consume messages from RabbitMQ and route them through the chain."""
    consumer = build_consumer()
    chain = build_processing_chain()
    use_case = ConsumeAndProcessUseCase(consumer, chain)

    result = use_case.execute(queue, limit)
    for message in result.messages:
        _print_message(message)
    typer.echo(
        typer.style(f"\nProcessed {len(result.messages)} message(s).", bold=True)
    )


@app.command()
def simulate(
    message_id: Annotated[str, typer.Option("--message-id", "-i")],
    payload: Annotated[
        str, typer.Option("--payload", "-p", help="JSON payload string")
    ],
) -> None:
    """Run a single in-memory message through the chain, without a broker."""
    chain = build_processing_chain()
    use_case = ProcessMessageUseCase(chain)

    message = IncomingMessage(message_id=message_id, payload=json.loads(payload))
    result = use_case.execute(message)
    _print_message(result)


if __name__ == "__main__":
    app()
