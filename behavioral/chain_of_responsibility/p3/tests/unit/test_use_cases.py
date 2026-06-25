"""Unit tests for the submit/get submission use cases."""

from __future__ import annotations

import pytest

from moderation.application.use_cases import (
    GetSubmissionUseCase,
    SubmissionNotFoundError,
    SubmitContentUseCase,
)
from moderation.domain.entities import ContentSubmission, ModerationStatus
from moderation.domain.interfaces import SubmissionRepository
from moderation.infrastructure.handlers import build_moderation_chain
from tests.conftest import FakeImageModerationClient


class InMemorySubmissionRepository(SubmissionRepository):
    """A dict-backed SubmissionRepository, used in place of Django ORM in tests."""

    def __init__(self) -> None:
        self._submissions: dict[str, ContentSubmission] = {}

    def save(self, submission: ContentSubmission) -> None:
        self._submissions[submission.submission_id] = submission

    def get(self, submission_id: str) -> ContentSubmission | None:
        return self._submissions.get(submission_id)


def test_submit_content_persists_moderated_submission() -> None:
    repository = InMemorySubmissionRepository()
    chain = build_moderation_chain(FakeImageModerationClient())
    use_case = SubmitContentUseCase(chain, repository)

    result = use_case.execute(author="alice", text="hello world")

    assert result.submission.status == ModerationStatus.APPROVED
    assert repository.get(result.submission.submission_id) is not None


def test_get_submission_returns_persisted_submission() -> None:
    repository = InMemorySubmissionRepository()
    chain = build_moderation_chain(FakeImageModerationClient())
    submit = SubmitContentUseCase(chain, repository)
    get_submission = GetSubmissionUseCase(repository)

    submitted = submit.execute(author="bob", text="hateSpeech here")

    fetched = get_submission.execute(submitted.submission.submission_id)

    assert fetched.submission_id == submitted.submission.submission_id
    assert fetched.status == ModerationStatus.REJECTED


def test_get_submission_raises_when_not_found() -> None:
    repository = InMemorySubmissionRepository()
    get_submission = GetSubmissionUseCase(repository)

    with pytest.raises(SubmissionNotFoundError):
        get_submission.execute("missing-id")
