"""Abstractions for the Command pattern: command, receiver, and publisher."""

from __future__ import annotations

from abc import ABC, abstractmethod


class TaskCommand(ABC):
    """Encapsulates a single unit of work as an object.

    Each concrete command wraps a receiver and the parameters needed to
    perform one task. Adding a new task type requires only a new
    subclass — no changes to the invoker or the use cases (OCP).
    """

    @abstractmethod
    def execute(self) -> str:
        """Perform the task against its receiver and return a result message."""

    @abstractmethod
    def get_command_name(self) -> str:
        """Return the stable name used to identify this command type."""

    @abstractmethod
    def to_payload(self) -> dict[str, object]:
        """Return the JSON-serialisable parameters needed to recreate this command."""


class TaskPublisher(ABC):
    """Boundary for publishing a command to a message broker for audit/replay."""

    @abstractmethod
    def publish(self, command_name: str, payload: dict[str, object]) -> None:
        """Publish a command's name and payload to the broker."""
