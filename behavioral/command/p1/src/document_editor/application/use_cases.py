"""Invoker and orchestration use cases for the Document Editor.

`HistoryInvoker` is the Command pattern's Invoker: it knows how to run a
command and keeps the undo/redo stacks, but it has zero knowledge of what
each command actually does to the document (that lives in `commands.py`).
"""

from __future__ import annotations

from document_editor.domain.entities import CommandInfo, CommandResult
from document_editor.domain.interfaces import CommandInvoker, DocumentCommand


class HistoryInvoker(CommandInvoker):
    """Maintains undo/redo stacks and command metadata for one document."""

    def __init__(self) -> None:
        self._undo_stack: list[tuple[DocumentCommand, CommandInfo]] = []
        self._redo_stack: list[tuple[DocumentCommand, CommandInfo]] = []

    def execute(self, command: DocumentCommand) -> CommandResult:
        """Run `command`, push it onto the undo stack and clear redo."""
        result = command.execute()
        info = CommandInfo(
            command_id=CommandInfo.new_id(),
            description=command.get_description(),
            is_reversible=command.is_reversible(),
        )
        self._undo_stack.append((command, info))
        self._redo_stack.clear()
        return result

    def undo(self) -> CommandResult | None:
        """Undo the most recent reversible command, moving it to redo."""
        entry = self._pop_reversible(self._undo_stack)
        if entry is None:
            return None
        command, info = entry
        result = command.undo()
        self._redo_stack.append((command, info))
        return result

    def redo(self) -> CommandResult | None:
        """Re-execute the most recently undone command."""
        if not self._redo_stack:
            return None
        command, info = self._redo_stack.pop()
        result = command.execute()
        self._undo_stack.append((command, info))
        return result

    def get_history(self) -> list[CommandInfo]:
        """Return metadata for every command currently in the undo stack."""
        return [info for _, info in self._undo_stack]

    def clear(self) -> None:
        """Discard both undo and redo stacks."""
        self._undo_stack.clear()
        self._redo_stack.clear()

    def _pop_reversible(
        self, stack: list[tuple[DocumentCommand, CommandInfo]]
    ) -> tuple[DocumentCommand, CommandInfo] | None:
        if not stack:
            return None
        return stack.pop()
