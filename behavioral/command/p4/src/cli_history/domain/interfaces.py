"""Abstractions for the Command pattern and its persistence boundaries."""

from __future__ import annotations

from abc import ABC, abstractmethod

from cli_history.domain.entities import CommandLogEntry, TodoList


class TodoCommand(ABC):
    """Encapsulates a single reversible operation on a TodoList.

    Adding a new operation requires only a new subclass — no changes to
    the invoker or the use cases (OCP).
    """

    @abstractmethod
    def execute(self, receiver: TodoList) -> None:
        """Apply the command to the receiver."""

    @abstractmethod
    def undo(self, receiver: TodoList) -> None:
        """Revert the command, restoring the previous state."""

    @abstractmethod
    def get_command_name(self) -> str:
        """Return the stable name used to identify this command type."""

    @abstractmethod
    def to_payload(self) -> dict[str, object]:
        """Return the JSON-serialisable parameters needed to recreate this command."""


class StateRepository(ABC):
    """Persistence boundary for the live TodoList state."""

    @abstractmethod
    def load(self) -> TodoList:
        """Load the current state, or an empty TodoList if none was saved yet."""

    @abstractmethod
    def save(self, state: TodoList) -> None:
        """Persist the current state."""


class CommandLogRepository(ABC):
    """Persistence boundary for the append-only command execution log."""

    @abstractmethod
    def append(self, command_name: str, payload: dict[str, object]) -> CommandLogEntry:
        """Append a new entry to the log and return it (with its assigned id)."""

    @abstractmethod
    def get_all(self) -> list[CommandLogEntry]:
        """Return every logged entry, ordered from oldest to newest."""
