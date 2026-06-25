"""Application use cases for the Text Editor Undo/Redo system.

Each use case has a single responsibility and depends only on the
EditorCaretaker abstraction (DIP). The TextDocument Originator is
reconstructed on demand from the current snapshot — SQLite is the
single source of truth, so there is no separate document repository.
"""

from __future__ import annotations

from text_editor_memento.domain.entities import (
    NoHistoryError,
    TextDocument,
    TextSnapshot,
)
from text_editor_memento.domain.interfaces import EditorCaretaker


class WriteContentUseCase:
    """Replaces the document's content and snapshots the result."""

    def __init__(self, caretaker: EditorCaretaker) -> None:
        self._caretaker = caretaker

    def execute(self, content: str) -> TextSnapshot:
        return self._caretaker.write(content)


class UndoEditUseCase:
    """Reverts the document to its previous snapshot."""

    def __init__(self, caretaker: EditorCaretaker) -> None:
        self._caretaker = caretaker

    def execute(self) -> TextSnapshot:
        return self._caretaker.undo()


class RedoEditUseCase:
    """Re-applies the next snapshot that was previously undone."""

    def __init__(self, caretaker: EditorCaretaker) -> None:
        self._caretaker = caretaker

    def execute(self) -> TextSnapshot:
        return self._caretaker.redo()


class GetCurrentContentUseCase:
    """Returns the document's current content, or an empty document if
    nothing has been written yet."""

    def __init__(self, caretaker: EditorCaretaker) -> None:
        self._caretaker = caretaker

    def execute(self) -> TextDocument:
        document = TextDocument()
        try:
            snapshot = self._caretaker.current()
        except NoHistoryError:
            return document
        document.restore(snapshot)
        return document


class GetHistoryUseCase:
    """Returns every snapshot ever recorded, oldest first."""

    def __init__(self, caretaker: EditorCaretaker) -> None:
        self._caretaker = caretaker

    def execute(self) -> list[TextSnapshot]:
        return self._caretaker.history()
