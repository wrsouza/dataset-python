"""Django ORM repository for WorkflowRequest.

OCP: a new state only needs an entry in `_STATE_REGISTRY` for the
repository to be able to rehydrate it; no other infrastructure code
changes.
"""

from __future__ import annotations

from workflow_approval_fsm.django_app.models import WorkflowRequestModel
from workflow_approval_fsm.domain.entities import WorkflowRequest
from workflow_approval_fsm.domain.interfaces import WorkflowState
from workflow_approval_fsm.infrastructure.states.approved import ApprovedState
from workflow_approval_fsm.infrastructure.states.draft import DraftState
from workflow_approval_fsm.infrastructure.states.pending_approval import (
    PendingApprovalState,
)
from workflow_approval_fsm.infrastructure.states.rejected import RejectedState

_STATE_REGISTRY: dict[str, type[WorkflowState]] = {
    "Draft": DraftState,
    "PendingApproval": PendingApprovalState,
    "Approved": ApprovedState,
    "Rejected": RejectedState,
}


class DjangoWorkflowRepository:
    def save(self, request: WorkflowRequest) -> None:
        WorkflowRequestModel.objects.update_or_create(
            request_id=request.request_id,
            defaults={
                "title": request.title,
                "state": request.get_current_state_name(),
            },
        )

    def find_by_id(self, request_id: str) -> WorkflowRequest | None:
        try:
            row = WorkflowRequestModel.objects.get(request_id=request_id)
        except WorkflowRequestModel.DoesNotExist:
            return None

        request = WorkflowRequest(request_id=row.request_id, title=row.title)
        request._state = _STATE_REGISTRY[row.state]()  # noqa: SLF001
        return request
