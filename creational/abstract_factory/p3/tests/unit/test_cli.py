"""Unit tests for the Typer CLI, using the InMemoryBrokerFactory via monkeypatch."""

from __future__ import annotations

from typer.testing import CliRunner

from broker_factory.cli import app
from broker_factory.infrastructure.factories import InMemoryBrokerFactory

runner = CliRunner()


def test_publish_command_succeeds(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        "broker_factory.cli.build_broker_factory",
        lambda *_args, **_kwargs: InMemoryBrokerFactory(),
    )

    result = runner.invoke(app, ["publish", "orders", "hello"])

    assert result.exit_code == 0
    assert "Published" in result.stdout


def test_consume_command_succeeds(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        "broker_factory.cli.build_broker_factory",
        lambda *_args, **_kwargs: InMemoryBrokerFactory(),
    )

    result = runner.invoke(app, ["consume", "orders"])

    assert result.exit_code == 0
    assert "Consumed" in result.stdout


def test_create_queue_command_succeeds(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        "broker_factory.cli.build_broker_factory",
        lambda *_args, **_kwargs: InMemoryBrokerFactory(),
    )

    result = runner.invoke(app, ["create-queue", "orders"])

    assert result.exit_code == 0
    assert "Created" in result.stdout


def test_list_queues_command_succeeds(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        "broker_factory.cli.build_broker_factory",
        lambda *_args, **_kwargs: InMemoryBrokerFactory(),
    )

    result = runner.invoke(app, ["list-queues"])

    assert result.exit_code == 0


def test_invalid_broker_exits_with_error(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    result = runner.invoke(app, ["publish", "orders", "hi", "--broker", "pulsar"])

    assert result.exit_code == 1
    assert "Error" in result.stdout
