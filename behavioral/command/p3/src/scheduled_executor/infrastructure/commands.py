"""Concrete commands and the registry used to build them from a payload."""

from __future__ import annotations

from collections.abc import Callable

from scheduled_executor.domain.interfaces import ScheduledCommand
from scheduled_executor.infrastructure.receivers import BackupReceiver, CleanupReceiver


class CleanupCommand(ScheduledCommand):
    """Encapsulates purging stale records."""

    def __init__(self, receiver: CleanupReceiver, older_than_days: int) -> None:
        self._receiver = receiver
        self._older_than_days = older_than_days

    def execute(self) -> str:
        return self._receiver.purge(self._older_than_days)

    def get_command_name(self) -> str:
        return "cleanup"


class BackupCommand(ScheduledCommand):
    """Encapsulates backing up a target dataset."""

    def __init__(self, receiver: BackupReceiver, target: str) -> None:
        self._receiver = receiver
        self._target = target

    def execute(self) -> str:
        return self._receiver.backup(self._target)

    def get_command_name(self) -> str:
        return "backup"


CommandFactory = Callable[[dict[str, object]], ScheduledCommand]


def _build_cleanup(payload: dict[str, object]) -> ScheduledCommand:
    older_than_days = payload.get("older_than_days", 30)
    assert isinstance(older_than_days, int)
    return CleanupCommand(receiver=CleanupReceiver(), older_than_days=older_than_days)


def _build_backup(payload: dict[str, object]) -> ScheduledCommand:
    return BackupCommand(receiver=BackupReceiver(), target=str(payload["target"]))


COMMAND_REGISTRY: dict[str, CommandFactory] = {
    "cleanup": _build_cleanup,
    "backup": _build_backup,
}


class UnknownCommandError(ValueError):
    """Raised when a command name has no matching factory in the registry."""


def build_command(command_name: str, payload: dict[str, object]) -> ScheduledCommand:
    """Build a concrete ScheduledCommand from its name and payload."""
    factory = COMMAND_REGISTRY.get(command_name)
    if factory is None:
        available = ", ".join(sorted(COMMAND_REGISTRY))
        raise UnknownCommandError(
            f"Unknown command '{command_name}'. Available: {available}"
        )
    return factory(payload)
