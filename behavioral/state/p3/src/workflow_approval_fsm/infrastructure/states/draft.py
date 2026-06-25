"""DraftState — initial state; the request is still being edited."""

from __future__ import annotations

from typing import TYPE_CHECKING

from workflow_approval_fsm.domain.interfaces import WorkflowState

if TYPE_CHECKING:
    from workflow_approval_fsm.domain.entities import WorkflowRequest


class DraftState(WorkflowState):
    """Request has been created but not yet sent for approval."""

    def submit(self, ctx: WorkflowRequest) -> None:
        from workflow_approval_fsm.infrastructure.states.pending_approval import (  # noqa: PLC0415
            PendingApprovalState,
        )

        ctx.transition_to(PendingApprovalState(), "submit")

    def get_name(self) -> str:
        return "Draft"

    def get_allowed_transitions(self) -> list[str]:
        return ["submit"]
