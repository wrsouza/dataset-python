"""Concrete commands for the Document Editor.

Each class encapsulates exactly one reversible operation against a
DocumentReceiver (Single Responsibility). New operations are added by
creating a new `DocumentCommand` subclass — no existing code changes
(Open/Closed).
"""

from __future__ import annotations

from document_editor.domain.entities import CommandResult
from document_editor.domain.interfaces import DocumentCommand, DocumentReceiver


class InsertTextCommand(DocumentCommand):
    """Inserts text at a given position; undo deletes it again."""

    def __init__(self, receiver: DocumentReceiver, position: int, text: str) -> None:
        self._receiver = receiver
        self._position = position
        self._text = text

    def execute(self) -> CommandResult:
        self._receiver.insert(self._position, self._text)
        return CommandResult(
            success=True,
            message=f"Inserted {len(self._text)!r} chars at {self._position}",
            content_snapshot=self._receiver.get_content(),
        )

    def undo(self) -> CommandResult:
        self._receiver.delete(self._position, self._position + len(self._text))
        return CommandResult(
            success=True,
            message=f"Undid insert at {self._position}",
            content_snapshot=self._receiver.get_content(),
        )

    def get_description(self) -> str:
        return f"Insert {len(self._text)} char(s) at position {self._position}"

    def is_reversible(self) -> bool:
        return True


class DeleteTextCommand(DocumentCommand):
    """Deletes a [start, end) range; undo re-inserts the captured text."""

    def __init__(self, receiver: DocumentReceiver, start: int, end: int) -> None:
        self._receiver = receiver
        self._start = start
        self._end = end
        self._deleted_text = ""

    def execute(self) -> CommandResult:
        self._deleted_text = self._receiver.delete(self._start, self._end)
        return CommandResult(
            success=True,
            message=f"Deleted range [{self._start}, {self._end})",
            content_snapshot=self._receiver.get_content(),
        )

    def undo(self) -> CommandResult:
        self._receiver.insert(self._start, self._deleted_text)
        return CommandResult(
            success=True,
            message=f"Undid delete at {self._start}",
            content_snapshot=self._receiver.get_content(),
        )

    def get_description(self) -> str:
        return f"Delete range [{self._start}, {self._end})"

    def is_reversible(self) -> bool:
        return True


class FormatCommand(DocumentCommand):
    """Applies inline formatting to a range; undo removes it again."""

    def __init__(
        self, receiver: DocumentReceiver, start: int, end: int, format_type: str
    ) -> None:
        self._receiver = receiver
        self._start = start
        self._end = end
        self._format_type = format_type

    def execute(self) -> CommandResult:
        self._receiver.apply_format(self._start, self._end, self._format_type)
        return CommandResult(
            success=True,
            message=f"Applied {self._format_type} to [{self._start}, {self._end})",
            content_snapshot=self._receiver.get_content(),
        )

    def undo(self) -> CommandResult:
        self._receiver.remove_format(self._start, self._end, self._format_type)
        return CommandResult(
            success=True,
            message=f"Removed {self._format_type} from [{self._start}, {self._end})",
            content_snapshot=self._receiver.get_content(),
        )

    def get_description(self) -> str:
        return f"Apply {self._format_type} to [{self._start}, {self._end})"

    def is_reversible(self) -> bool:
        return True
