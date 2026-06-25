"""Integration tests for DjangoSubmissionRepository against a real ORM."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from moderation.domain.entities import (
    ContentSubmission,
    ModerationStatus,
    ModerationStep,
)
from moderation.infrastructure.repository import DjangoSubmissionRepository

pytestmark = pytest.mark.django_db


def _resolved_submission() -> ContentSubmission:
    submission = ContentSubmission(
        submission_id="sub-1", author="alice", text="hello world"
    )
    submission.record_step(
        ModerationStep(
            handler_name="ManualReviewHandler",
            action=ModerationStatus.APPROVED,
            reason="Passed automated checks.",
            handled_at=datetime(2026, 1, 1, tzinfo=UTC),
        )
    )
    return submission


def test_save_and_get_round_trips_submission() -> None:
    repository = DjangoSubmissionRepository()
    submission = _resolved_submission()

    repository.save(submission)
    fetched = repository.get(submission.submission_id)

    assert fetched is not None
    assert fetched.status == ModerationStatus.APPROVED
    assert fetched.history[0].handler_name == "ManualReviewHandler"


def test_get_returns_none_when_missing() -> None:
    repository = DjangoSubmissionRepository()

    assert repository.get("unknown") is None


def test_save_updates_existing_submission() -> None:
    repository = DjangoSubmissionRepository()
    submission = _resolved_submission()
    repository.save(submission)

    submission.text = "updated text"
    repository.save(submission)
    fetched = repository.get(submission.submission_id)

    assert fetched is not None
    assert fetched.text == "updated text"
