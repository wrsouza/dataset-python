"""Unit tests for the concrete commands and the command registry."""

from __future__ import annotations

import pytest

from cli_history.domain.entities import TodoList
from cli_history.infrastructure.commands import (
    AddItemCommand,
    RemoveItemCommand,
    UnknownCommandError,
    build_command,
)


def test_add_item_command_execute_and_undo() -> None:
    state = TodoList()
    command = AddItemCommand("Buy milk")

    command.execute(state)
    assert state.items == ["Buy milk"]

    command.undo(state)
    assert state.items == []
    assert command.get_command_name() == "add"
    assert command.to_payload() == {"item": "Buy milk"}


def test_remove_item_command_execute_and_undo() -> None:
    state = TodoList(items=["Buy milk"])
    command = RemoveItemCommand("Buy milk")

    command.execute(state)
    assert state.items == []

    command.undo(state)
    assert state.items == ["Buy milk"]
    assert command.get_command_name() == "remove"


def test_build_command_resolves_add() -> None:
    command = build_command("add", {"item": "Walk dog"})

    assert isinstance(command, AddItemCommand)


def test_build_command_resolves_remove() -> None:
    command = build_command("remove", {"item": "Walk dog"})

    assert isinstance(command, RemoveItemCommand)


def test_build_command_raises_for_unknown_name() -> None:
    with pytest.raises(UnknownCommandError):
        build_command("nope", {})
