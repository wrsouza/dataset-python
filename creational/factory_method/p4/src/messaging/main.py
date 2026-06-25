"""CLI entry point — Typer-based message consumer CLI.

Composition root: the only place where concrete factories are selected.
All use cases receive abstractions (DIP).

Usage:
    python -m messaging.main consume --broker kafka --topic orders --group my-group
    python -m messaging.main consume --broker rabbitmq --queue payments --limit 100
    python -m messaging.main brokers
"""
from __future__ import annotations

import json
from typing import Annotated, Optional

import typer

from messaging.application.use_cases import (
    ConsumeMessagesUseCase,
    ListBrokersUseCase,
    StreamMessagesUseCase,
)
from messaging.domain.entities import BrokerType, ConsumeConfig
from messaging.infrastructure.consumers import CONSUMER_FACTORY_REGISTRY

app = typer.Typer(
    name="message-consumer",
    help="Factory Method demo: consume messages from Kafka, RabbitMQ, or SQS.",
    add_completion=False,
)


def _get_factory(broker: str) -> object:
    """Resolve a factory from the registry or raise a user-friendly error."""
    factory = CONSUMER_FACTORY_REGISTRY.get(broker)
    if factory is None:
        available = ", ".join(CONSUMER_FACTORY_REGISTRY.keys())
        typer.echo(
            typer.style(
                f"Unknown broker '{broker}'. Available: {available}",
                fg=typer.colors.RED,
                bold=True,
            )
        )
        raise typer.Exit(code=1)
    return factory


@app.command()
def consume(
    broker: Annotated[
        str,
        typer.Option("--broker", "-b", help="Broker type: kafka | rabbitmq | sqs"),
    ] = "kafka",
    topic: Annotated[
        Optional[str],
        typer.Option("--topic", "-t", help="Kafka topic name"),
    ] = None,
    queue: Annotated[
        Optional[str],
        typer.Option("--queue", "-q", help="RabbitMQ / SQS queue name"),
    ] = None,
    group: Annotated[
        str,
        typer.Option("--group", "-g", help="Consumer group ID (Kafka)"),
    ] = "default-group",
    limit: Annotated[
        Optional[int],
        typer.Option("--limit", "-l", help="Max messages to consume (0 = unlimited)"),
    ] = 10,
    timeout: Annotated[
        float,
        typer.Option("--timeout", help="Poll timeout in seconds"),
    ] = 5.0,
    stream: Annotated[
        bool,
        typer.Option("--stream", help="Stream messages one by one (lazy mode)"),
    ] = False,
) -> None:
    """Consume messages from a broker using the Factory Method pattern.

    Examples:

        consume --broker kafka --topic orders --group my-group

        consume --broker rabbitmq --queue payments --limit 100

        consume --broker sqs --queue notifications --stream
    """
    topic_or_queue = topic or queue
    if topic_or_queue is None:
        typer.echo(
            typer.style(
                "Provide --topic (Kafka) or --queue (RabbitMQ / SQS).",
                fg=typer.colors.RED,
            )
        )
        raise typer.Exit(code=1)

    # Validate broker type (OCP: registry handles the rest)
    try:
        BrokerType(broker)
    except ValueError:
        available = ", ".join(b.value for b in BrokerType)
        typer.echo(
            typer.style(
                f"Invalid broker '{broker}'. Choose from: {available}",
                fg=typer.colors.RED,
            )
        )
        raise typer.Exit(code=1)

    factory = _get_factory(broker)  # type: ignore[assignment]

    config = ConsumeConfig(
        broker=BrokerType(broker),
        topic_or_queue=topic_or_queue,
        group_id=group,
        limit=limit if limit != 0 else None,
        timeout_seconds=timeout,
    )

    broker_name = factory.get_broker_name()  # type: ignore[union-attr]
    typer.echo(
        typer.style(f"[{broker_name}]", fg=typer.colors.GREEN, bold=True)
        + f" Consuming from '{topic_or_queue}'"
        + (f" (limit={limit})" if limit else " (unlimited)")
    )

    count = 0
    if stream:
        use_case = StreamMessagesUseCase(factory)  # type: ignore[arg-type]
        for message, consumer in use_case.execute(config):
            _print_message(message, count)
            consumer.ack(message)
            count += 1
    else:
        use_case_batch = ConsumeMessagesUseCase(factory)  # type: ignore[arg-type]
        messages = use_case_batch.execute(config)
        for message in messages:
            _print_message(message, count)
            count += 1

    typer.echo(
        typer.style(f"\nConsumed {count} message(s).", fg=typer.colors.BRIGHT_CYAN)
    )


@app.command()
def brokers() -> None:
    """List all available broker factories."""
    use_case = ListBrokersUseCase(CONSUMER_FACTORY_REGISTRY)
    items = use_case.execute()

    typer.echo(typer.style("Available brokers:", bold=True))
    for item in items:
        typer.echo(f"  {typer.style(item['slug'], fg=typer.colors.YELLOW)} → {item['name']}")


def _print_message(message: object, index: int) -> None:
    """Print a single message to stdout in a readable format."""
    from messaging.domain.entities import Message as Msg

    assert isinstance(message, Msg)
    typer.echo(f"\n  [{index}] topic={message.topic} key={message.key}")
    try:
        decoded = message.decode_value()
        parsed = json.loads(decoded)
        typer.echo(f"       value={json.dumps(parsed, indent=8)}")
    except (UnicodeDecodeError, json.JSONDecodeError):
        typer.echo(f"       value={message.value!r}")
    typer.echo(f"       ts={message.timestamp.isoformat()} headers={message.headers}")


if __name__ == "__main__":
    app()
