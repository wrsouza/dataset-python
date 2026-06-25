"""CLI entry point — Typer-based cloud event notifier over AWS SNS.

Composition root: the only place where the concrete SNS client and the
local ConsoleObserver are wired together. All use cases receive
abstractions (DIP).

Usage:
    python -m cloud_event_notifier.main order.created '{"order_id": "o1"}'

Note: Typer flattens a single-command app — since `publish` is the
only command registered, its name is not part of the invocation.
"""

from __future__ import annotations

import json

import typer

from cloud_event_notifier.application.use_cases import PublishEventUseCase
from cloud_event_notifier.infrastructure.factory import build_publisher
from cloud_event_notifier.infrastructure.observers import ConsoleObserver

app = typer.Typer(
    name="cloud-event-notifier",
    help="Observer pattern demo: publish events locally and to AWS SNS.",
    add_completion=False,
)


@app.command()
def publish(event_type: str, payload: str) -> None:
    """Publish a JSON payload as a `event_type` cloud event."""
    publisher = build_publisher()
    publisher.subscribe(ConsoleObserver(writer=typer.echo))

    use_case = PublishEventUseCase(publisher)
    event = use_case.execute(event_type, json.loads(payload))

    typer.echo(f"Published {event.event_id} to SNS.")


if __name__ == "__main__":
    app()
