"""Unit tests for the moderation chain handlers."""

from __future__ import annotations

from moderation.domain.entities import ContentSubmission, ModerationStatus
from moderation.infrastructure.handlers import build_moderation_chain
from tests.conftest import FakeImageModerationClient


def _submission(
    text: str = "hello world", image_bytes: bytes | None = None
) -> ContentSubmission:
    return ContentSubmission(
        submission_id="s-1", author="alice", text=text, image_bytes=image_bytes
    )


def test_clean_text_without_image_is_approved() -> None:
    chain = build_moderation_chain(FakeImageModerationClient())

    submission = chain.handle(_submission())

    assert submission.status == ModerationStatus.APPROVED
    assert len(submission.history) == 1
    assert submission.history[0].handler_name == "ManualReviewHandler"


def test_banned_word_is_rejected_at_text_stage() -> None:
    chain = build_moderation_chain(FakeImageModerationClient())

    submission = chain.handle(_submission(text="this is spam content"))

    assert submission.status == ModerationStatus.REJECTED
    assert submission.history[0].handler_name == "TextProfanityHandler"
    assert "spam" in submission.history[0].reason


def test_unsafe_image_is_rejected_at_image_stage() -> None:
    chain = build_moderation_chain(
        FakeImageModerationClient(labels=["Explicit Nudity"])
    )

    submission = chain.handle(_submission(image_bytes=b"fake-bytes"))

    assert submission.status == ModerationStatus.REJECTED
    assert submission.history[0].handler_name == "ImageSafetyHandler"
    assert "Explicit Nudity" in submission.history[0].reason


def test_clean_image_passes_through_to_manual_review() -> None:
    chain = build_moderation_chain(FakeImageModerationClient(labels=[]))

    submission = chain.handle(_submission(image_bytes=b"fake-bytes"))

    assert submission.status == ModerationStatus.APPROVED


def test_text_rejection_takes_priority_over_image_check() -> None:
    chain = build_moderation_chain(
        FakeImageModerationClient(labels=["Explicit Nudity"])
    )

    submission = chain.handle(_submission(text="scam alert", image_bytes=b"fake-bytes"))

    assert submission.history[0].handler_name == "TextProfanityHandler"
