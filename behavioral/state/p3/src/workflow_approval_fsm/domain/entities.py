"""Domain entities for the Workflow Approval FSM."""

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
class WorkflowRequest:
    """Context in the State pattern.

    Delegates all behaviour to the current _state object.
    """

    from workflow_approval_fsm.domain.interfaces import WorkflowState  # noqa: PLC0415

    request_id: str
    title: str
    history: list[StateTransitionRecord] = field(default_factory=list)
    _state: WorkflowState = field(init=False)

    def __post_init__(self) -> None:
        from workflow_approval_fsm.infrastructure.states.draft import (  # noqa: PLC0415
            DraftState,
        )

        self._state = DraftState()

    # ── State delegation ────────────────────────────────────────────────────────

    def submit(self) -> None:
        self._state.submit(self)

    def approve(self) -> None:
        self._state.approve(self)

    def reject(self) -> None:
        self._state.reject(self)

    def request_changes(self) -> None:
        self._state.request_changes(self)

    # ── State accessors ─────────────────────────────────────────────────────────

    def get_current_state_name(self) -> str:
        return self._state.get_name()

    def get_allowed_transitions(self) -> list[str]:
        return self._state.get_allowed_transitions()

    def transition_to(self, new_state: WorkflowState, action: str) -> None:
        """Record the transition and swap the current state."""
        record = StateTransitionRecord(
            from_state=self._state.get_name(),
            to_state=new_state.get_name(),
            action=action,
        )
        self.history.append(record)
        self._state = new_state
