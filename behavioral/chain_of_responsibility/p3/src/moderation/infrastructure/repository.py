"""Django ORM-backed implementation of SubmissionRepository."""

from __future__ import annotations

from datetime import datetime

from moderation.domain.entities import (
    ContentSubmission,
    ModerationStatus,
    ModerationStep,
)
from moderation.domain.interfaces import SubmissionRepository
from moderation.infrastructure.models import SubmissionModel


def _serialize_history(history: list[ModerationStep]) -> list[dict[str, str]]:
    return [
        {
            "handler_name": step.handler_name,
            "action": step.action.value,
            "reason": step.reason,
            "handled_at": step.handled_at.isoformat(),
        }
        for step in history
    ]


def _deserialize_history(raw: list[dict[str, str]]) -> list[ModerationStep]:
    return [
        ModerationStep(
            handler_name=item["handler_name"],
            action=ModerationStatus(item["action"]),
            reason=item["reason"],
            handled_at=datetime.fromisoformat(item["handled_at"]),
        )
        for item in raw
    ]


class DjangoSubmissionRepository(SubmissionRepository):
    """Persists content submissions via the Django ORM."""

    def save(self, submission: ContentSubmission) -> None:
        SubmissionModel.objects.update_or_create(
            submission_id=submission.submission_id,
            defaults={
                "author": submission.author,
                "text": submission.text,
                "status": submission.status.value,
                "history": _serialize_history(submission.history),
            },
        )

    def get(self, submission_id: str) -> ContentSubmission | None:
        record = SubmissionModel.objects.filter(submission_id=submission_id).first()
        if record is None:
            return None
        return ContentSubmission(
            submission_id=record.submission_id,
            author=record.author,
            text=record.text,
            status=ModerationStatus(record.status),
            history=_deserialize_history(record.history),
        )
