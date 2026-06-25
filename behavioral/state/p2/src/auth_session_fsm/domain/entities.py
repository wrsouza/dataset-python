"""Domain entities for the User Auth Session FSM."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

MAX_FAILED_ATTEMPTS = 3


@dataclass
class StateTransitionRecord:
    from_state: str
    to_state: str
    action: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class AuthSession:
    """Context in the State pattern.

    Delegates all behaviour to the current _state object.
    """

    from auth_session_fsm.domain.interfaces import SessionState  # noqa: PLC0415

    session_id: str
    failed_attempts: int = 0
    history: list[StateTransitionRecord] = field(default_factory=list)
    _state: SessionState = field(init=False)

    def __post_init__(self) -> None:
        from auth_session_fsm.infrastructure.states.anonymous import (  # noqa: PLC0415
            AnonymousState,
        )

        self._state = AnonymousState()

    # ── State delegation ────────────────────────────────────────────────────────

    def login(self, success: bool) -> None:
        self._state.login(self, success)

    def logout(self) -> None:
        self._state.logout(self)

    def refresh(self) -> None:
        self._state.refresh(self)

    def expire(self) -> None:
        self._state.expire(self)

    def unlock(self) -> None:
        self._state.unlock(self)

    # ── State accessors ─────────────────────────────────────────────────────────

    def get_current_state_name(self) -> str:
        return self._state.get_name()

    def get_allowed_transitions(self) -> list[str]:
        return self._state.get_allowed_transitions()

    def transition_to(self, new_state: SessionState, action: str) -> None:
        """Record the transition and swap the current state."""
        record = StateTransitionRecord(
            from_state=self._state.get_name(),
            to_state=new_state.get_name(),
            action=action,
        )
        self.history.append(record)
        self._state = new_state
