"""CLI entry point — Typer-based messaging client.

Composition root: the only place where a concrete Adapter is selected
from the registry. Every command below depends solely on the
``MessageBroker`` Target (DIP) — never on pika or kafka-python.

Usage:
    python -m messaging_adapter.main publish --broker rabbitmq \
        --topic payments --message '{"x":1}'
    python -m messaging_adapter.main consume --broker kafka \
        --topic orders --limit 5
    python -m messaging_adapter.main brokers
"""

from __future__ import annotations

import json
from typing import Annotated

import typer

from messaging_adapter.application.use_cases import (
    ConsumeMessagesUseCase,
    ListBrokersUseCase,
    PublishMessageUseCase,
)
from messaging_adapter.domain.entities import BrokerType, ConsumeConfig, PublishConfig
from messaging_adapter.infrastructure.registry import (
    BROKER_DISPLAY_NAMES,
    build_broker_registry,
)

app = typer.Typer(
    name="messaging-adapter",
    help="Adapter pattern demo: publish/consume via RabbitMQ or Kafka, one interface.",
    add_completion=False,
)


def _resolve_broker_type(broker: str) -> BrokerType:
    """Validate the CLI --broker option, or exit with a friendly error."""
    try:
        return BrokerType(broker)
    except ValueError:
        available = ", ".join(b.value for b in BrokerType)
        typer.echo(
            typer.style(
                f"Invalid broker '{broker}'. Choose from: {available}",
                fg=typer.colors.RED,
            )
        )
        raise typer.Exit(code=1) from None


@app.command()
def publish(
    broker: Annotated[
        str, typer.Option("--broker", "-b", help="Broker type: rabbitmq | kafka")
    ] = "rabbitmq",
    topic: Annotated[
        str, typer.Option("--topic", "-t", help="Topic / queue name")
    ] = "default-topic",
    message: Annotated[
        str, typer.Option("--message", "-m", help="Message payload (text)")
    ] = "{}",
    key: Annotated[
        str | None, typer.Option("--key", "-k", help="Optional message key")
    ] = None,
) -> None:
    """Publish a message to a broker through the MessageBroker Target."""
    broker_type = _resolve_broker_type(broker)
    registry = build_broker_registry()
    adapter = registry[broker_type]

    config = PublishConfig(broker=broker_type, topic=topic, key=key)
    use_case = PublishMessageUseCase(adapter)
    sent = use_case.execute(config, message.encode())

    broker_name = BROKER_DISPLAY_NAMES[broker_type]
    typer.echo(
        typer.style(f"[{broker_name}]", fg=typer.colors.GREEN, bold=True)
        + f" Published to '{topic}': {sent.decode_value()}"
    )


@app.command()
def consume(
    broker: Annotated[
        str, typer.Option("--broker", "-b", help="Broker type: rabbitmq | kafka")
    ] = "rabbitmq",
    topic: Annotated[
        str, typer.Option("--topic", "-t", help="Topic / queue name")
    ] = "default-topic",
    group: Annotated[
        str, typer.Option("--group", "-g", help="Consumer group ID (Kafka)")
    ] = "default-group",
    limit: Annotated[
        int | None,
        typer.Option("--limit", "-l", help="Max messages to consume (0 = unlimited)"),
    ] = 10,
    timeout: Annotated[
        float, typer.Option("--timeout", help="Poll timeout in seconds")
    ] = 5.0,
) -> None:
    """Consume messages from a broker through the MessageBroker Target."""
    broker_type = _resolve_broker_type(broker)
    registry = build_broker_registry()
    adapter = registry[broker_type]

    config = ConsumeConfig(
        broker=broker_type,
        topic=topic,
        group_id=group,
        limit=limit if limit else None,
        timeout_seconds=timeout,
    )
    use_case = ConsumeMessagesUseCase(adapter)
    messages = use_case.execute(config)

    broker_name = BROKER_DISPLAY_NAMES[broker_type]
    typer.echo(
        typer.style(f"[{broker_name}]", fg=typer.colors.GREEN, bold=True)
        + f" Consuming from '{topic}'"
        + (f" (limit={limit})" if limit else " (unlimited)")
    )
    for index, msg in enumerate(messages):
        _print_message(msg, index)

    typer.echo(
        typer.style(
            f"\nConsumed {len(messages)} message(s).", fg=typer.colors.BRIGHT_CYAN
        )
    )


@app.command()
def brokers() -> None:
    """List all available broker Adapters."""
    use_case = ListBrokersUseCase(BROKER_DISPLAY_NAMES)
    items = use_case.execute()

    typer.echo(typer.style("Available brokers:", bold=True))
    for item in items:
        typer.echo(
            f"  {typer.style(item['slug'], fg=typer.colors.YELLOW)} -> {item['name']}"
        )


def _print_message(message: object, index: int) -> None:
    """Print a single consumed message to stdout in a readable format."""
    from messaging_adapter.domain.entities import Message as Msg

    assert isinstance(message, Msg)
    typer.echo(f"\n  [{index}] topic={message.topic} key={message.key}")
    try:
        decoded = message.decode_value()
        parsed = json.loads(decoded)
        typer.echo(f"       value={json.dumps(parsed, indent=8)}")
    except (UnicodeDecodeError, json.JSONDecodeError):
        typer.echo(f"       value={message.value!r}")
    typer.echo(f"       headers={message.headers}")


if __name__ == "__main__":
    app()
