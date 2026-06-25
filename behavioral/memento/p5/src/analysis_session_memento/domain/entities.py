"""Domain entities for the Analysis Session Snapshots system."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class AnalysisSnapshot:
    """Immutable snapshot of an analysis session's parameters and results.

    frozen=True enforces the Memento pattern guarantee: once captured,
    a snapshot cannot be mutated — only read or discarded.
    """

    parameters: dict[str, Any]
    results: dict[str, Any]
    version: int
    label: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if self.version < 1:
            raise ValueError(f"version must be >= 1, got {self.version}")
        if not self.label.strip():
            raise ValueError("label cannot be empty")


@dataclass
class AnalysisSession:
    """Originator — holds the current parameters/results of an analysis run.

    SRP: AnalysisSession only manages its own in-memory state. It does
    not persist itself — that is the caretaker's job.
    """

    session_id: str
    parameters: dict[str, Any]
    results: dict[str, Any]
    current_version: int = 0
    _label: str = field(default="autosave", repr=False)

    def set_label(self, label: str) -> None:
        """Set the label for the next snapshot (e.g. 'autosave', 'manual')."""
        self._label = label

    def create_snapshot(self) -> AnalysisSnapshot:
        """Capture current parameters/results into an immutable snapshot."""
        return AnalysisSnapshot(
            parameters=dict(self.parameters),
            results=dict(self.results),
            version=self.current_version,
            label=self._label,
        )

    def restore(self, snapshot: AnalysisSnapshot) -> None:
        """Restore state from a previously captured snapshot.

        The AnalysisSession does not know how the snapshot was stored —
        that is the Caretaker's concern (Separation of Concerns / SRP).
        """
        self.parameters = dict(snapshot.parameters)
        self.results = dict(snapshot.results)
        self.current_version = snapshot.version

    def update(self, parameters: dict[str, Any], results: dict[str, Any]) -> None:
        """Apply a new run's parameters/results, advancing the version."""
        self.parameters = parameters
        self.results = results
        self.current_version += 1


class NoHistoryError(Exception):
    """Raised when undo is requested but no previous snapshot exists."""

    def __init__(self, session_id: str) -> None:
        super().__init__(f"No history available for session '{session_id}'")
        self.session_id = session_id
