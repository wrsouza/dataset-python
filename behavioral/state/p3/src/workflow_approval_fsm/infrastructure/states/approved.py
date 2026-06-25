"""ApprovedState — terminal state for an accepted request."""

from __future__ import annotations

from workflow_approval_fsm.domain.interfaces import WorkflowState


class ApprovedState(WorkflowState):
    """Request was approved; no further transitions are allowed."""

    def get_name(self) -> str:
        return "Approved"

    def get_allowed_transitions(self) -> list[str]:
        return []
