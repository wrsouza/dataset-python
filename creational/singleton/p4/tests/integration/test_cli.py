"""Integration tests for the Typer CLI using CliRunner end-to-end."""

from __future__ import annotations

import json

from typer.testing import CliRunner

from src.cli.main import app

runner = CliRunner()


def test_log_command_prints_json_line_to_stdout() -> None:
    result = runner.invoke(app, ["log", "hello world", "--level", "INFO"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload["message"] == "hello world"
    assert payload["level"] == "INFO"


def test_log_command_accepts_tags_as_context() -> None:
    result = runner.invoke(
        app, ["log", "order created", "--tag", "order_id=42", "--level", "INFO"]
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload["context"]["order_id"] == "42"


def test_log_command_rejects_invalid_level() -> None:
    result = runner.invoke(app, ["log", "oops", "--level", "NOPE"])

    assert result.exit_code != 0


def test_log_command_rejects_malformed_tag() -> None:
    result = runner.invoke(app, ["log", "oops", "--tag", "not-a-pair"])

    assert result.exit_code != 0


def test_context_command_reports_updated_context() -> None:
    result = runner.invoke(app, ["context", "service=billing"])

    assert result.exit_code == 0
    assert "service" in result.stdout


def test_stats_command_reports_counters_after_logging() -> None:
    runner.invoke(app, ["log", "first", "--level", "INFO"])
    result = runner.invoke(app, ["stats"])

    assert result.exit_code == 0
    assert "records_emitted" in result.stdout
