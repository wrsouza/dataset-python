"""Unit tests for DjangoWorkflowRepository against a real (in-memory SQLite) ORM."""

from __future__ import annotations

import pytest

from workflow_approval_fsm.domain.entities import WorkflowRequest
from workflow_approval_fsm.infrastructure.repository import DjangoWorkflowRepository

pytestmark = pytest.mark.django_db


def test_save_and_find_round_trips_state() -> None:
    repository = DjangoWorkflowRepository()
    request = WorkflowRequest(request_id="r1", title="Buy laptops")
    request.submit()
    repository.save(request)

    found = repository.find_by_id("r1")

    assert found is not None
    assert found.title == "Buy laptops"
    assert found.get_current_state_name() == "PendingApproval"


def test_find_returns_none_for_unknown_request() -> None:
    repository = DjangoWorkflowRepository()

    assert repository.find_by_id("unknown") is None


def test_save_overwrites_existing_request_state() -> None:
    repository = DjangoWorkflowRepository()
    request = WorkflowRequest(request_id="r1", title="Buy laptops")
    repository.save(request)

    request.submit()
    repository.save(request)

    found = repository.find_by_id("r1")
    assert found is not None
    assert found.get_current_state_name() == "PendingApproval"
