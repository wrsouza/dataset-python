"""Domain interfaces for the Form State Save/Restore system.

Defines the Memento pattern contracts: Originator and Caretaker.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

from form_state_memento.domain.entities import FormSnapshot


@runtime_checkable
class SnapshotProtocol(Protocol):
    """Memento protocol — snapshot is immutable and self-describing."""

    @property
    def step(self) -> int: ...

    @property
    def label(self) -> str: ...


class FormCaretaker(ABC):
    """Caretaker ABC — manages the lifecycle of form snapshots.

    SRP: only stores/retrieves snapshots, has no knowledge of form field
    semantics.
    OCP: new storage backends extend this without modifying existing code.
    """

    @abstractmethod
    def save(self, session_id: str, snapshot: FormSnapshot) -> None:
        """Persist a snapshot for a given form session."""
        ...

    @abstractmethod
    def undo(self, session_id: str) -> FormSnapshot:
        """Return the previous snapshot (one step back), discarding the latest."""
        ...

    @abstractmethod
    def latest(self, session_id: str) -> FormSnapshot:
        """Return the most recent snapshot for a session."""
        ...

    @abstractmethod
    def history(self, session_id: str) -> list[FormSnapshot]:
        """Return all snapshots for a session, ordered oldest to newest."""
        ...
