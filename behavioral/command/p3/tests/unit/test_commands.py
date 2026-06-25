"""Unit tests for the concrete commands and the command registry."""

from __future__ import annotations

import pytest

from scheduled_executor.infrastructure.commands import (
    BackupCommand,
    CleanupCommand,
    UnknownCommandError,
    build_command,
)
from scheduled_executor.infrastructure.receivers import BackupReceiver, CleanupReceiver


def test_cleanup_command_executes_via_receiver() -> None:
    command = CleanupCommand(CleanupReceiver(), older_than_days=7)

    result = command.execute()

    assert "7" in result
    assert command.get_command_name() == "cleanup"


def test_backup_command_executes_via_receiver() -> None:
    command = BackupCommand(BackupReceiver(), target="orders-db")

    result = command.execute()

    assert "orders-db" in result
    assert command.get_command_name() == "backup"


def test_build_command_resolves_cleanup_with_default_days() -> None:
    command = build_command("cleanup", {})

    assert isinstance(command, CleanupCommand)
    assert "30" in command.execute()


def test_build_command_resolves_backup() -> None:
    command = build_command("backup", {"target": "users-db"})

    assert isinstance(command, BackupCommand)


def test_build_command_raises_for_unknown_name() -> None:
    with pytest.raises(UnknownCommandError):
        build_command("delete_everything", {})
