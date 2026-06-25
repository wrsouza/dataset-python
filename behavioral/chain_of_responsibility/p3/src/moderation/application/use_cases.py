"""Use cases orchestrating submission creation and moderation through the chain."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from moderation.domain.entities import ContentSubmission
from moderation.domain.interfaces import ModerationHandler, SubmissionRepository


class SubmissionNotFoundError(Exception):
    """Raised when a submission id has no matching record."""


@dataclass
class SubmitContentResult:
    """Outcome returned to callers after submitting content for moderation."""

    submission: ContentSubmission


class SubmitContentUseCase:
    """Creates a submission and routes it through the moderation chain."""

    def __init__(
        self, chain: ModerationHandler, repository: SubmissionRepository
    ) -> None:
        self._chain = chain
        self._repository = repository

    def execute(
        self, author: str, text: str, image_bytes: bytes | None = None
    ) -> SubmitContentResult:
        submission = ContentSubmission(
            submission_id=str(uuid.uuid4()),
            author=author,
            text=text,
            image_bytes=image_bytes,
        )
        moderated = self._chain.handle(submission)
        self._repository.save(moderated)
        return SubmitContentResult(submission=moderated)


class GetSubmissionUseCase:
    """Fetches a previously submitted piece of content by id."""

    def __init__(self, repository: SubmissionRepository) -> None:
        self._repository = repository

    def execute(self, submission_id: str) -> ContentSubmission:
        submission = self._repository.get(submission_id)
        if submission is None:
            raise SubmissionNotFoundError(f"Submission {submission_id} not found")
        return submission
