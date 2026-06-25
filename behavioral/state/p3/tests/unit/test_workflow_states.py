"""Unit tests for the WorkflowRequest State pattern implementation."""

from __future__ import annotations

import pytest

from workflow_approval_fsm.domain.entities import WorkflowRequest
from workflow_approval_fsm.domain.interfaces import InvalidTransitionError


def test_new_request_starts_in_draft() -> None:
    request = WorkflowRequest(request_id="r1", title="Buy laptops")

    assert request.get_current_state_name() == "Draft"
    assert request.get_allowed_transitions() == ["submit"]


def test_submit_transitions_to_pending_approval() -> None:
    request = WorkflowRequest(request_id="r1", title="Buy laptops")

    request.submit()

    assert request.get_current_state_name() == "PendingApproval"


def test_approve_transitions_to_approved() -> None:
    request = WorkflowRequest(request_id="r1", title="Buy laptops")
    request.submit()

    request.approve()

    assert request.get_current_state_name() == "Approved"
    assert request.get_allowed_transitions() == []


def test_reject_transitions_to_rejected() -> None:
    request = WorkflowRequest(request_id="r1", title="Buy laptops")
    request.submit()

    request.reject()

    assert request.get_current_state_name() == "Rejected"


def test_request_changes_returns_to_draft() -> None:
    request = WorkflowRequest(request_id="r1", title="Buy laptops")
    request.submit()

    request.request_changes()

    assert request.get_current_state_name() == "Draft"


def test_draft_rejects_approve() -> None:
    request = WorkflowRequest(request_id="r1", title="Buy laptops")

    with pytest.raises(InvalidTransitionError):
        request.approve()


def test_approved_is_terminal() -> None:
    request = WorkflowRequest(request_id="r1", title="Buy laptops")
    request.submit()
    request.approve()

    with pytest.raises(InvalidTransitionError):
        request.reject()


def test_rejected_is_terminal() -> None:
    request = WorkflowRequest(request_id="r1", title="Buy laptops")
    request.submit()
    request.reject()

    with pytest.raises(InvalidTransitionError):
        request.submit()


def test_history_records_each_transition() -> None:
    request = WorkflowRequest(request_id="r1", title="Buy laptops")

    request.submit()
    request.reject()

    assert [record.action for record in request.history] == ["submit", "reject"]
