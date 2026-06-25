"""Core entities for the CLI history / replay domain."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TodoList:
    """The Receiver: a simple mutable list of to-do items.

    Knows only how to mutate itself — it has no notion of history,
    undo, or replay. That responsibility belongs to commands and the
    invoker/use cases built on top of it.
    """

    items: list[str] = field(default_factory=list)

    def add(self, item: str) -> None:
        self.items.append(item)

    def remove(self, item: str) -> None:
        self.items.remove(item)


@dataclass
class CommandLogEntry:
    """A single recorded execution of a command, kept for history/replay."""

    entry_id: int
    command_name: str
    payload: dict[str, object]
    executed_at: datetime
