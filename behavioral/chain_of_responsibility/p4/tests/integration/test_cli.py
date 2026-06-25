"""Integration tests for the Typer CLI `simulate` command."""

from __future__ import annotations

import json

import pytest
from typer.testing import CliRunner

from message_pipeline.infrastructure.rabbitmq_consumer import RabbitMQQueueConsumer
from message_pipeline.main import app
from tests.unit.test_rabbitmq_consumer import FakeChannel

runner = CliRunner()


def test_simulate_processes_valid_message() -> None:
    result = runner.invoke(
        app,
        [
            "simulate",
            "--message-id",
            "m-1",
            "--payload",
            '{"order_id": "o-1", "amount": 42}',
        ],
    )

    assert result.exit_code == 0
    assert "processed" in result.stdout


def test_simulate_rejects_message_missing_fields() -> None:
    result = runner.invoke(
        app,
        ["simulate", "--message-id", "m-2", "--payload", "{}"],
    )

    assert result.exit_code == 0
    assert "rejected" in result.stdout


def test_process_command_consumes_and_routes_messages(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import message_pipeline.main as main_module

    fake_channel = FakeChannel(
        [json.loads('{"message_id": "m-3", "order_id": "o-3", "amount": 5}')]
    )

    def fake_build_consumer() -> RabbitMQQueueConsumer:
        return RabbitMQQueueConsumer(fake_channel)

    monkeypatch.setattr(main_module, "build_consumer", fake_build_consumer)

    result = runner.invoke(app, ["process", "--queue", "orders", "--limit", "5"])

    assert result.exit_code == 0
    assert "Processed 1 message(s)" in result.stdout
