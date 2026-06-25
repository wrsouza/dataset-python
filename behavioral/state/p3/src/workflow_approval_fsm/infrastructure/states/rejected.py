"""RejectedState — terminal state for a declined request."""

from __future__ import annotations

from workflow_approval_fsm.domain.interfaces import WorkflowState


class RejectedState(WorkflowState):
    """Request was rejected; no further transitions are allowed."""

    def get_name(self) -> str:
        return "Rejected"

    def get_allowed_transitions(self) -> list[str]:
        return []
