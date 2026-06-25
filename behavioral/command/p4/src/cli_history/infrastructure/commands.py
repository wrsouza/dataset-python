"""Concrete commands and the registry used to rebuild them for replay."""

from __future__ import annotations

from collections.abc import Callable

from cli_history.domain.entities import TodoList
from cli_history.domain.interfaces import TodoCommand


class AddItemCommand(TodoCommand):
    """Encapsulates adding one item to the to-do list."""

    def __init__(self, item: str) -> None:
        self._item = item

    def execute(self, receiver: TodoList) -> None:
        receiver.add(self._item)

    def undo(self, receiver: TodoList) -> None:
        receiver.remove(self._item)

    def get_command_name(self) -> str:
        return "add"

    def to_payload(self) -> dict[str, object]:
        return {"item": self._item}


class RemoveItemCommand(TodoCommand):
    """Encapsulates removing one item from the to-do list."""

    def __init__(self, item: str) -> None:
        self._item = item

    def execute(self, receiver: TodoList) -> None:
        receiver.remove(self._item)

    def undo(self, receiver: TodoList) -> None:
        receiver.add(self._item)

    def get_command_name(self) -> str:
        return "remove"

    def to_payload(self) -> dict[str, object]:
        return {"item": self._item}


CommandFactory = Callable[[dict[str, object]], TodoCommand]

COMMAND_REGISTRY: dict[str, CommandFactory] = {
    "add": lambda payload: AddItemCommand(str(payload["item"])),
    "remove": lambda payload: RemoveItemCommand(str(payload["item"])),
}


class UnknownCommandError(ValueError):
    """Raised when a command name has no matching factory in the registry."""


def build_command(command_name: str, payload: dict[str, object]) -> TodoCommand:
    """Build a concrete TodoCommand from its name and payload via the registry."""
    factory = COMMAND_REGISTRY.get(command_name)
    if factory is None:
        available = ", ".join(sorted(COMMAND_REGISTRY))
        raise UnknownCommandError(
            f"Unknown command '{command_name}'. Available: {available}"
        )
    return factory(payload)
