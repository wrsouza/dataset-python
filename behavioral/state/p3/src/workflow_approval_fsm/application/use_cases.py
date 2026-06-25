"""Application use cases for the Workflow Approval FSM.

Each use case has a single responsibility and depends only on
DjangoWorkflowRepository's public contract plus the notification
task — dispatched as a Celery task so notifying approvers/requesters
never blocks the HTTP response.
"""

from __future__ import annotations

from dataclasses import dataclass

from workflow_approval_fsm.domain.entities import WorkflowRequest
from workflow_approval_fsm.infrastructure.celery_app import notify_task
from workflow_approval_fsm.infrastructure.repository import DjangoWorkflowRepository


class WorkflowRequestNotFoundError(Exception):
    def __init__(self, request_id: str) -> None:
        super().__init__(f"Workflow request '{request_id}' not found")
        self.request_id = request_id


@dataclass
class CreateWorkflowRequestInput:
    request_id: str
    title: str


class CreateWorkflowRequestUseCase:
    def __init__(self, repository: DjangoWorkflowRepository) -> None:
        self._repository = repository

    def execute(self, data: CreateWorkflowRequestInput) -> WorkflowRequest:
        request = WorkflowRequest(request_id=data.request_id, title=data.title)
        self._repository.save(request)
        return request


class TransitionUseCase:
    """Base for the four transition use cases — load, transition, persist,
    notify. Subclasses only specify which WorkflowRequest method to call
    and the notification message."""

    action_message: str

    def __init__(self, repository: DjangoWorkflowRepository) -> None:
        self._repository = repository

    def _apply(self, request: WorkflowRequest) -> None:
        raise NotImplementedError

    def execute(self, request_id: str) -> WorkflowRequest:
        request = self._repository.find_by_id(request_id)
        if request is None:
            raise WorkflowRequestNotFoundError(request_id)

        self._apply(request)
        self._repository.save(request)
        notify_task.delay(request_id, self.action_message.format(title=request.title))
        return request


class SubmitWorkflowRequestUseCase(TransitionUseCase):
    action_message = "Workflow request '{title}' submitted for approval"

    def _apply(self, request: WorkflowRequest) -> None:
        request.submit()


class ApproveWorkflowRequestUseCase(TransitionUseCase):
    action_message = "Workflow request '{title}' approved"

    def _apply(self, request: WorkflowRequest) -> None:
        request.approve()


class RejectWorkflowRequestUseCase(TransitionUseCase):
    action_message = "Workflow request '{title}' rejected"

    def _apply(self, request: WorkflowRequest) -> None:
        request.reject()


class RequestChangesUseCase(TransitionUseCase):
    action_message = "Changes requested for workflow request '{title}'"

    def _apply(self, request: WorkflowRequest) -> None:
        request.request_changes()


class GetWorkflowRequestUseCase:
    def __init__(self, repository: DjangoWorkflowRepository) -> None:
        self._repository = repository

    def execute(self, request_id: str) -> WorkflowRequest | None:
        return self._repository.find_by_id(request_id)
