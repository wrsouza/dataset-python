"""HTTP views exposing the Content Export Visitor system."""

from __future__ import annotations

import json

from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from content_export_visitor.application.use_cases import (
    ExportContentInput,
    ExportContentUseCase,
    GetExportJobUseCase,
)
from content_export_visitor.domain.entities import ExportJob
from content_export_visitor.domain.exceptions import (
    ExportJobNotFoundError,
    InvalidFormatError,
    InvalidNodeTypeError,
)
from content_export_visitor.infrastructure.repository import DjangoExportJobRepository
from content_export_visitor.infrastructure.s3_factory import build_s3_client


def _job_to_dict(job: ExportJob) -> dict[str, object]:
    return {
        "job_id": job.job_id,
        "format": job.format_name,
        "s3_key": job.s3_key,
        "created_at": job.created_at.isoformat(),
    }


@csrf_exempt
@require_http_methods(["POST"])
def export_content(request: HttpRequest, format_name: str) -> JsonResponse:
    """POST /exports/<format_name>/"""
    payload = json.loads(request.body or "{}")
    use_case = ExportContentUseCase(
        DjangoExportJobRepository(), build_s3_client(), settings.S3_BUCKET
    )
    try:
        job = use_case.execute(
            ExportContentInput(format_name=format_name, nodes=payload["nodes"])
        )
    except (InvalidFormatError, InvalidNodeTypeError) as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    return JsonResponse(_job_to_dict(job), status=201)


@require_http_methods(["GET"])
def get_export_job(request: HttpRequest, job_id: str) -> JsonResponse:
    """GET /exports/jobs/<job_id>/"""
    use_case = GetExportJobUseCase(DjangoExportJobRepository())
    try:
        job = use_case.execute(job_id)
    except ExportJobNotFoundError as exc:
        return JsonResponse({"error": str(exc)}, status=404)
    return JsonResponse(_job_to_dict(job))
