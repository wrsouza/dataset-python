"""Concrete moderation handlers ordered text -> image -> manual review."""

from __future__ import annotations

from datetime import UTC, datetime

from moderation.domain.entities import (
    ContentSubmission,
    ModerationStatus,
    ModerationStep,
)
from moderation.domain.interfaces import ModerationHandler
from moderation.infrastructure.rekognition_client import ImageModerationClient

DEFAULT_BANNED_WORDS = frozenset({"spam", "scam", "hatespeech"})


class TextProfanityHandler(ModerationHandler):
    """Rejects submissions whose text contains a banned word."""

    def __init__(self, banned_words: frozenset[str] = DEFAULT_BANNED_WORDS) -> None:
        self._banned_words = banned_words

    def _inspect(self, submission: ContentSubmission) -> ModerationStep | None:
        lowered = submission.text.lower()
        hit = next((word for word in self._banned_words if word in lowered), None)
        if hit is None:
            return None
        return ModerationStep(
            handler_name=self.__class__.__name__,
            action=ModerationStatus.REJECTED,
            reason=f"Text contains banned term: '{hit}'",
            handled_at=datetime.now(UTC),
        )


class ImageSafetyHandler(ModerationHandler):
    """Rejects submissions whose image is flagged unsafe by Rekognition."""

    def __init__(self, client: ImageModerationClient) -> None:
        self._client = client

    def _inspect(self, submission: ContentSubmission) -> ModerationStep | None:
        if submission.image_bytes is None:
            return None
        labels = self._client.detect_unsafe_labels(submission.image_bytes)
        if not labels:
            return None
        return ModerationStep(
            handler_name=self.__class__.__name__,
            action=ModerationStatus.REJECTED,
            reason=f"Image flagged for: {', '.join(labels)}",
            handled_at=datetime.now(UTC),
        )


class ManualReviewHandler(ModerationHandler):
    """Final link: approves anything that passed all automated checks."""

    def _inspect(self, submission: ContentSubmission) -> ModerationStep | None:
        return ModerationStep(
            handler_name=self.__class__.__name__,
            action=ModerationStatus.APPROVED,
            reason="Passed automated text and image checks.",
            handled_at=datetime.now(UTC),
        )


def build_moderation_chain(image_client: ImageModerationClient) -> ModerationHandler:
    """Wire the default text -> image -> manual-review chain."""
    text_handler = TextProfanityHandler()
    image_handler = ImageSafetyHandler(image_client)
    manual_review = ManualReviewHandler()
    text_handler.set_next(image_handler).set_next(manual_review)
    return text_handler
