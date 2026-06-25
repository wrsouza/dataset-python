"""PendingApprovalState — awaiting a reviewer's decision."""

from __future__ import annotations

from typing import TYPE_CHECKING

from workflow_approval_fsm.domain.interfaces import WorkflowState

if TYPE_CHECKING:
    from workflow_approval_fsm.domain.entities import WorkflowRequest


class PendingApprovalState(WorkflowState):
    """Request was submitted and is waiting for an approve/reject decision."""

    def approve(self, ctx: WorkflowRequest) -> None:
        from workflow_approval_fsm.infrastructure.states.approved import (  # noqa: PLC0415
            ApprovedState,
        )

        ctx.transition_to(ApprovedState(), "approve")

    def reject(self, ctx: WorkflowRequest) -> None:
        from workflow_approval_fsm.infrastructure.states.rejected import (  # noqa: PLC0415
            RejectedState,
        )

        ctx.transition_to(RejectedState(), "reject")

    def request_changes(self, ctx: WorkflowRequest) -> None:
        from workflow_approval_fsm.infrastructure.states.draft import (  # noqa: PLC0415
            DraftState,
        )

        ctx.transition_to(DraftState(), "request_changes")

    def get_name(self) -> str:
        return "PendingApproval"

    def get_allowed_transitions(self) -> list[str]:
        return ["approve", "reject", "request_changes"]
