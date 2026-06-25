"""Use cases orchestrating command execution, logging, and replay."""

from __future__ import annotations

from cli_history.domain.entities import CommandLogEntry, TodoList
from cli_history.domain.interfaces import CommandLogRepository, StateRepository
from cli_history.infrastructure.commands import build_command


class ExecuteCommandUseCase:
    """Loads the live state, applies a command, persists state and log entry."""

    def __init__(
        self, state_repository: StateRepository, log_repository: CommandLogRepository
    ) -> None:
        self._state_repository = state_repository
        self._log_repository = log_repository

    def execute(self, command_name: str, payload: dict[str, object]) -> TodoList:
        command = build_command(command_name, payload)
        state = self._state_repository.load()
        command.execute(state)
        self._state_repository.save(state)
        self._log_repository.append(command_name, command.to_payload())
        return state


class UndoLastCommandUseCase:
    """Reverts the most recently executed command, if any."""

    def __init__(
        self, state_repository: StateRepository, log_repository: CommandLogRepository
    ) -> None:
        self._state_repository = state_repository
        self._log_repository = log_repository

    def execute(self) -> TodoList:
        entries = self._log_repository.get_all()
        state = self._state_repository.load()
        if not entries:
            return state
        last_entry = entries[-1]
        command = build_command(last_entry.command_name, last_entry.payload)
        command.undo(state)
        self._state_repository.save(state)
        return state


class GetHistoryUseCase:
    """Returns every command ever executed, oldest first."""

    def __init__(self, log_repository: CommandLogRepository) -> None:
        self._log_repository = log_repository

    def execute(self) -> list[CommandLogEntry]:
        return self._log_repository.get_all()


class ReplayHistoryUseCase:
    """Rebuilds a fresh TodoList by replaying the full command log from scratch.

    This never touches the live state — it proves that the log alone is
    enough to reconstruct the current state, the core idea behind
    command-log-based replay.
    """

    def __init__(self, log_repository: CommandLogRepository) -> None:
        self._log_repository = log_repository

    def execute(self) -> TodoList:
        state = TodoList()
        for entry in self._log_repository.get_all():
            command = build_command(entry.command_name, entry.payload)
            command.execute(state)
        return state
