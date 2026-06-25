"""Abstractions for the Chain of Responsibility moderation handlers."""

from __future__ import annotations

from abc import ABC, abstractmethod

from moderation.domain.entities import ContentSubmission, ModerationStep


class ModerationHandler(ABC):
    """A single link in the content moderation chain.

    Each handler inspects the submission and decides whether it can
    reach a final verdict. If not, it forwards the submission to the
    next handler in the chain, if any.
    """

    _next_handler: ModerationHandler | None = None

    def set_next(self, handler: ModerationHandler) -> ModerationHandler:
        """Wire the next handler in the chain and return it for fluent chaining."""
        self._next_handler = handler
        return handler

    def handle(self, submission: ContentSubmission) -> ContentSubmission:
        """Attempt to reach a verdict, otherwise pass it along the chain."""
        verdict = self._inspect(submission)
        if verdict is not None:
            submission.record_step(verdict)
            return submission
        if self._next_handler is not None:
            return self._next_handler.handle(submission)
        return submission

    @abstractmethod
    def _inspect(self, submission: ContentSubmission) -> ModerationStep | None:
        """Return a ModerationStep verdict, or None to defer to the next handler."""


class SubmissionRepository(ABC):
    """Persistence boundary for content submissions."""

    @abstractmethod
    def save(self, submission: ContentSubmission) -> None:
        """Persist the current state of a submission."""

    @abstractmethod
    def get(self, submission_id: str) -> ContentSubmission | None:
        """Retrieve a submission by its identifier, if it exists."""
