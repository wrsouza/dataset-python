"""Domain interfaces for the Text Editor Undo/Redo system.

Defines the Memento pattern contract: the Caretaker.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from text_editor_memento.domain.entities import TextSnapshot


class EditorCaretaker(ABC):
    """Caretaker ABC — manages the lifecycle of document snapshots,
    including the undo/redo pointer.

    SRP: only stores/retrieves snapshots and tracks the current position
    in the history; has no knowledge of how content is edited.
    OCP: new storage backends extend this without modifying existing code.
    """

    @abstractmethod
    def write(self, content: str) -> TextSnapshot:
        """Record a new edit, discarding any redo branch ahead of it."""
        ...

    @abstractmethod
    def undo(self) -> TextSnapshot:
        """Move the pointer one step back and return that snapshot."""
        ...

    @abstractmethod
    def redo(self) -> TextSnapshot:
        """Move the pointer one step forward and return that snapshot."""
        ...

    @abstractmethod
    def current(self) -> TextSnapshot:
        """Return the snapshot the pointer currently sits on."""
        ...

    @abstractmethod
    def history(self) -> list[TextSnapshot]:
        """Return all snapshots ever recorded, ordered oldest to newest."""
        ...
