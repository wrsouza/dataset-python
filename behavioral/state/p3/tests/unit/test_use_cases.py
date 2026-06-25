"""Unit tests for the Workflow Approval FSM use cases.

CELERY_TASK_ALWAYS_EAGER (set in config.settings_test) makes the
notification task run synchronously in-process, so these tests never
need a real Redis broker.
"""

from __future__ import annotations

import pytest

from workflow_approval_fsm.application.use_cases import (
    ApproveWorkflowRequestUseCase,
    CreateWorkflowRequestInput,
    CreateWorkflowRequestUseCase,
    GetWorkflowRequestUseCase,
    RejectWorkflowRequestUseCase,
    RequestChangesUseCase,
    SubmitWorkflowRequestUseCase,
    WorkflowRequestNotFoundError,
)
from workflow_approval_fsm.django_app.models import NotificationLogModel
from workflow_approval_fsm.domain.interfaces import InvalidTransitionError
from workflow_approval_fsm.infrastructure.repository import DjangoWorkflowRepository

pytestmark = pytest.mark.django_db


def test_create_workflow_request_persists_in_draft() -> None:
    repository = DjangoWorkflowRepository()
    use_case = CreateWorkflowRequestUseCase(repository)

    request = use_case.execute(
        CreateWorkflowRequestInput(request_id="r1", title="Buy laptops")
    )

    assert request.get_current_state_name() == "Draft"
    assert repository.find_by_id("r1") is not None


def test_submit_use_case_transitions_and_notifies() -> None:
    repository = DjangoWorkflowRepository()
    CreateWorkflowRequestUseCase(repository).execute(
        CreateWorkflowRequestInput(request_id="r1", title="Buy laptops")
    )

    request = SubmitWorkflowRequestUseCase(repository).execute("r1")

    assert request.get_current_state_name() == "PendingApproval"
    assert NotificationLogModel.objects.filter(request_id="r1").count() == 1


def test_approve_use_case_transitions_and_notifies() -> None:
    repository = DjangoWorkflowRepository()
    CreateWorkflowRequestUseCase(repository).execute(
        CreateWorkflowRequestInput(request_id="r1", title="Buy laptops")
    )
    SubmitWorkflowRequestUseCase(repository).execute("r1")

    request = ApproveWorkflowRequestUseCase(repository).execute("r1")

    assert request.get_current_state_name() == "Approved"


def test_reject_use_case_transitions_and_notifies() -> None:
    repository = DjangoWorkflowRepository()
    CreateWorkflowRequestUseCase(repository).execute(
        CreateWorkflowRequestInput(request_id="r1", title="Buy laptops")
    )
    SubmitWorkflowRequestUseCase(repository).execute("r1")

    request = RejectWorkflowRequestUseCase(repository).execute("r1")

    assert request.get_current_state_name() == "Rejected"


def test_request_changes_use_case_returns_to_draft() -> None:
    repository = DjangoWorkflowRepository()
    CreateWorkflowRequestUseCase(repository).execute(
        CreateWorkflowRequestInput(request_id="r1", title="Buy laptops")
    )
    SubmitWorkflowRequestUseCase(repository).execute("r1")

    request = RequestChangesUseCase(repository).execute("r1")

    assert request.get_current_state_name() == "Draft"


def test_transition_on_unknown_request_raises() -> None:
    repository = DjangoWorkflowRepository()

    with pytest.raises(WorkflowRequestNotFoundError):
        SubmitWorkflowRequestUseCase(repository).execute("unknown")


def test_invalid_transition_raises() -> None:
    repository = DjangoWorkflowRepository()
    CreateWorkflowRequestUseCase(repository).execute(
        CreateWorkflowRequestInput(request_id="r1", title="Buy laptops")
    )

    with pytest.raises(InvalidTransitionError):
        ApproveWorkflowRequestUseCase(repository).execute("r1")


def test_get_workflow_request_use_case_returns_none_for_unknown() -> None:
    repository = DjangoWorkflowRepository()

    assert GetWorkflowRequestUseCase(repository).execute("unknown") is None
