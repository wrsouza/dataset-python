"""Domain entities for the Form State Save/Restore system."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class FormSnapshot:
    """Immutable snapshot of a form's field values at a point in time.

    frozen=True enforces the Memento pattern guarantee: once captured,
    a snapshot cannot be mutated — only read or discarded.
    """

    fields: dict[str, Any]
    step: int
    label: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if self.step < 1:
            raise ValueError(f"step must be >= 1, got {self.step}")
        if not self.label.strip():
            raise ValueError("label cannot be empty")


@dataclass
class FormSession:
    """Originator — holds the current draft of a multi-step form.

    SRP: FormSession only manages its own field state.
    It does not persist itself — that is the caretaker's job.
    """

    session_id: str
    fields: dict[str, Any]
    current_step: int = 1
    _label: str = field(default="autosave", repr=False)

    def set_label(self, label: str) -> None:
        """Set the label for the next snapshot (e.g. 'autosave', 'manual')."""
        self._label = label

    def create_snapshot(self) -> FormSnapshot:
        """Capture current field values into an immutable FormSnapshot."""
        return FormSnapshot(
            fields=dict(self.fields),
            step=self.current_step,
            label=self._label,
        )

    def restore(self, snapshot: FormSnapshot) -> None:
        """Restore field values from a previously captured snapshot.

        The FormSession does not know how the snapshot was stored — that
        is the Caretaker's concern (Separation of Concerns / SRP).
        """
        self.fields = dict(snapshot.fields)
        self.current_step = snapshot.step

    def update_fields(self, new_fields: dict[str, Any], new_step: int) -> None:
        """Apply new field values, moving the form to a new step."""
        self.fields = {**self.fields, **new_fields}
        self.current_step = new_step


class SessionNotFoundError(Exception):
    """Raised when a form session does not exist in the repository."""

    def __init__(self, session_id: str) -> None:
        super().__init__(f"Form session '{session_id}' not found")
        self.session_id = session_id


class NoHistoryError(Exception):
    """Raised when undo is requested but no previous snapshot exists."""

    def __init__(self, session_id: str) -> None:
        super().__init__(f"No history available for session '{session_id}'")
        self.session_id = session_id
