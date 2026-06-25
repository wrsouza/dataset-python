"""CLI tests for P5 — Messaging Protocol Adapter.

Exercises the Typer composition root end-to-end in simulation mode
(no real broker required) to cover ``main.py``'s command wiring.
"""

from __future__ import annotations

from typer.testing import CliRunner

from messaging_adapter.main import app

runner = CliRunner()


class TestPublishCommand:
    def test_publish_to_rabbitmq_succeeds(self) -> None:
        result = runner.invoke(
            app,
            [
                "publish",
                "--broker",
                "rabbitmq",
                "--topic",
                "payments",
                "--message",
                '{"amount": 10}',
            ],
        )
        assert result.exit_code == 0
        assert "RabbitMQ" in result.stdout
        assert "Published" in result.stdout

    def test_publish_to_kafka_succeeds(self) -> None:
        result = runner.invoke(
            app,
            ["publish", "--broker", "kafka", "--topic", "orders", "-m", "{}"],
        )
        assert result.exit_code == 0
        assert "Kafka" in result.stdout

    def test_publish_with_invalid_broker_exits_with_error(self) -> None:
        result = runner.invoke(app, ["publish", "--broker", "sqs"])
        assert result.exit_code == 1
        assert "Invalid broker" in result.stdout


class TestConsumeCommand:
    def test_consume_from_rabbitmq_prints_messages(self) -> None:
        result = runner.invoke(
            app,
            ["consume", "--broker", "rabbitmq", "--topic", "payments", "--limit", "2"],
        )
        assert result.exit_code == 0
        assert "Consuming from 'payments'" in result.stdout
        assert "Consumed 2 message(s)." in result.stdout

    def test_consume_from_kafka_prints_messages(self) -> None:
        result = runner.invoke(
            app,
            ["consume", "--broker", "kafka", "--topic", "orders", "--limit", "1"],
        )
        assert result.exit_code == 0
        assert "Consumed 1 message(s)." in result.stdout

    def test_consume_with_unlimited_flag(self) -> None:
        result = runner.invoke(
            app,
            ["consume", "--broker", "rabbitmq", "--topic", "payments", "--limit", "0"],
        )
        assert result.exit_code == 0
        assert "(unlimited)" in result.stdout

    def test_consume_with_invalid_broker_exits_with_error(self) -> None:
        result = runner.invoke(app, ["consume", "--broker", "sqs"])
        assert result.exit_code == 1


class TestBrokersCommand:
    def test_brokers_lists_rabbitmq_and_kafka(self) -> None:
        result = runner.invoke(app, ["brokers"])
        assert result.exit_code == 0
        assert "rabbitmq" in result.stdout
        assert "kafka" in result.stdout
