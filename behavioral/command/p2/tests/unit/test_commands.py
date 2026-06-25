"""Unit tests for the concrete commands and the command registry."""

from __future__ import annotations

import pytest

from task_command_queue.infrastructure.commands import (
    GenerateReportCommand,
    SendEmailCommand,
    UnknownCommandError,
    build_command,
)
from task_command_queue.infrastructure.receivers import EmailReceiver, ReportReceiver


def test_send_email_command_executes_via_receiver() -> None:
    command = SendEmailCommand(EmailReceiver(), "a@b.com", "Hi", "Hello there")

    result = command.execute()

    assert "a@b.com" in result
    assert command.get_command_name() == "send_email"
    assert command.to_payload() == {
        "to": "a@b.com",
        "subject": "Hi",
        "body": "Hello there",
    }


def test_generate_report_command_executes_via_receiver() -> None:
    command = GenerateReportCommand(ReportReceiver(), "sales", {"month": "june"})

    result = command.execute()

    assert "sales" in result
    assert command.get_command_name() == "generate_report"
    assert command.to_payload() == {
        "report_type": "sales",
        "parameters": {"month": "june"},
    }


def test_build_command_resolves_send_email() -> None:
    command = build_command(
        "send_email", {"to": "x@y.com", "subject": "S", "body": "B"}
    )

    assert isinstance(command, SendEmailCommand)


def test_build_command_resolves_generate_report() -> None:
    command = build_command(
        "generate_report", {"report_type": "usage", "parameters": {}}
    )

    assert isinstance(command, GenerateReportCommand)


def test_build_command_raises_for_unknown_name() -> None:
    with pytest.raises(UnknownCommandError):
        build_command("delete_universe", {})
