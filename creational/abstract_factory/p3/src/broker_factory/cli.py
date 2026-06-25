"""Typer CLI entry point for the Message Broker Factory.

Composition root: this is the only module that imports `build_broker_factory`
directly. All use cases depend solely on the MessageBrokerFactory abstraction.
"""

from __future__ import annotations

import os

import typer
from rich.console import Console

from broker_factory.application.use_cases import (
    ConsumeMessagesUseCase,
    CreateQueueUseCase,
    ListQueuesUseCase,
    PublishMessageUseCase,
)
from broker_factory.domain.interfaces import MessageBrokerFactory
from broker_factory.infrastructure.factories import build_broker_factory

app = typer.Typer(
    name="broker-factory",
    help="Demonstrates the Abstract Factory pattern across message brokers.",
    no_args_is_help=True,
)
console = Console()

RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://app:secret@rabbitmq:5672/")
KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
LOCALSTACK_URL = os.environ.get("LOCALSTACK_URL", "http://localstack:4566")

BrokerOption = typer.Option(
    "rabbitmq",
    "--broker",
    "-b",
    help="Broker family to use: rabbitmq, kafka or sqs.",
)


def _build_factory(broker: str) -> MessageBrokerFactory:
    """Resolve the MessageBrokerFactory for the requested broker name."""
    try:
        return build_broker_factory(
            broker,
            rabbitmq_url=RABBITMQ_URL,
            kafka_servers=KAFKA_BOOTSTRAP_SERVERS,
            localstack_url=LOCALSTACK_URL,
        )
    except ValueError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc


@app.command()
def publish(
    destination: str = typer.Argument(..., help="Queue/topic name."),
    message: str = typer.Argument(..., help="Message body to publish."),
    broker: str = BrokerOption,
) -> None:
    """Publish a message to the given broker's queue/topic."""
    factory = _build_factory(broker)
    use_case = PublishMessageUseCase(factory)
    result = use_case.execute(destination, message)
    console.print(f"[green]Published[/green] to {result.broker}: {result.to_dict()}")


@app.command()
def consume(
    source: str = typer.Argument(..., help="Queue/topic name."),
    max_messages: int = typer.Option(10, "--max", "-m", help="Max messages to pull."),
    broker: str = BrokerOption,
) -> None:
    """Consume messages from the given broker's queue/topic."""
    factory = _build_factory(broker)
    use_case = ConsumeMessagesUseCase(factory)
    result = use_case.execute(source, max_messages)
    console.print(f"[green]Consumed[/green] from {result.broker}: {result.to_dict()}")


@app.command("create-queue")
def create_queue(
    name: str = typer.Argument(..., help="Queue/topic name to create."),
    broker: str = BrokerOption,
) -> None:
    """Create a queue/topic on the given broker."""
    factory = _build_factory(broker)
    use_case = CreateQueueUseCase(factory)
    result = use_case.execute(name)
    console.print(f"[green]Created[/green]: {result}")


@app.command("list-queues")
def list_queues(broker: str = BrokerOption) -> None:
    """List all queues/topics on the given broker."""
    factory = _build_factory(broker)
    use_case = ListQueuesUseCase(factory)
    result = use_case.execute()
    console.print(result)


if __name__ == "__main__":
    app()
