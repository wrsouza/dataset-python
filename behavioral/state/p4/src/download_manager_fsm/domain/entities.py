"""Domain entities for the Download Manager State machine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class StateTransitionRecord:
    from_state: str
    to_state: str
    action: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class DownloadJob:
    """Context in the State pattern.

    Delegates all behaviour to the current _state object.
    """

    from download_manager_fsm.domain.interfaces import DownloadState  # noqa: PLC0415

    job_id: str
    s3_key: str
    bytes_downloaded: int = 0
    failure_reason: str = ""
    history: list[StateTransitionRecord] = field(default_factory=list)
    _state: DownloadState = field(init=False)

    def __post_init__(self) -> None:
        from download_manager_fsm.infrastructure.states.idle import (  # noqa: PLC0415
            IdleState,
        )

        self._state = IdleState()

    # ── State delegation ────────────────────────────────────────────────────────

    def start(self) -> None:
        self._state.start(self)

    def pause(self) -> None:
        self._state.pause(self)

    def resume(self) -> None:
        self._state.resume(self)

    def complete(self, bytes_downloaded: int) -> None:
        self._state.complete(self, bytes_downloaded)

    def fail(self, reason: str) -> None:
        self._state.fail(self, reason)

    def retry(self) -> None:
        self._state.retry(self)

    # ── State accessors ─────────────────────────────────────────────────────────

    def get_current_state_name(self) -> str:
        return self._state.get_name()

    def get_allowed_transitions(self) -> list[str]:
        return self._state.get_allowed_transitions()

    def transition_to(self, new_state: DownloadState, action: str) -> None:
        """Record the transition and swap the current state."""
        record = StateTransitionRecord(
            from_state=self._state.get_name(),
            to_state=new_state.get_name(),
            action=action,
        )
        self.history.append(record)
        self._state = new_state
