"""Domain interfaces for the Analysis Session Snapshots system.

Defines the Memento pattern contract: the Caretaker.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from analysis_session_memento.domain.entities import AnalysisSnapshot


class AnalysisCaretaker(ABC):
    """Caretaker ABC — manages the lifecycle of analysis snapshots.

    SRP: only stores/retrieves snapshots, has no knowledge of what the
    analysis parameters/results actually mean.
    OCP: new storage backends extend this without modifying existing code.
    """

    @abstractmethod
    def save(self, session_id: str, snapshot: AnalysisSnapshot) -> None:
        """Persist a snapshot for a given analysis session."""
        ...

    @abstractmethod
    def undo(self, session_id: str) -> AnalysisSnapshot:
        """Discard the latest snapshot and return the previous one."""
        ...

    @abstractmethod
    def latest(self, session_id: str) -> AnalysisSnapshot:
        """Return the most recent snapshot for a session."""
        ...

    @abstractmethod
    def history(self, session_id: str) -> list[AnalysisSnapshot]:
        """Return all snapshots for a session, ordered oldest to newest."""
        ...
