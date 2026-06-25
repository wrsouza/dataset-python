"""Django views for content moderation — Client of the Chain of Responsibility."""

from __future__ import annotations

import base64
import json

from django.http import HttpRequest, HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from moderation.application.use_cases import (
    GetSubmissionUseCase,
    SubmissionNotFoundError,
    SubmitContentUseCase,
)
from moderation.domain.entities import ContentSubmission
from moderation.infrastructure.factory import build_chain
from moderation.infrastructure.repository import DjangoSubmissionRepository

_repository = DjangoSubmissionRepository()


def _submission_to_dict(submission: ContentSubmission) -> dict[str, object]:
    return {
        "submission_id": submission.submission_id,
        "author": submission.author,
        "text": submission.text,
        "status": submission.status.value,
        "history": [
            {
                "handler_name": step.handler_name,
                "action": step.action.value,
                "reason": step.reason,
                "handled_at": step.handled_at.isoformat(),
            }
            for step in submission.history
        ],
    }


def _json(data: object, status: int = 200) -> HttpResponse:
    return HttpResponse(
        json.dumps(data), content_type="application/json", status=status
    )


@method_decorator(csrf_exempt, name="dispatch")
class SubmitContentView(View):
    """POST /submissions/ — submits content for moderation."""

    def post(self, request: HttpRequest) -> HttpResponse:
        payload = json.loads(request.body)
        image_b64 = payload.get("image_base64")
        image_bytes = base64.b64decode(image_b64) if image_b64 else None

        use_case = SubmitContentUseCase(build_chain(), _repository)
        result = use_case.execute(
            author=payload["author"], text=payload["text"], image_bytes=image_bytes
        )
        return _json(_submission_to_dict(result.submission), status=201)


class SubmissionDetailView(View):
    """GET /submissions/<submission_id>/ — fetches a moderated submission."""

    def get(self, request: HttpRequest, submission_id: str) -> HttpResponse:
        use_case = GetSubmissionUseCase(_repository)
        try:
            submission = use_case.execute(submission_id)
        except SubmissionNotFoundError as exc:
            return _json({"error": str(exc)}, status=404)
        return _json(_submission_to_dict(submission))
