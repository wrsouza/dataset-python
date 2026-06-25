"""Django views — client code that depends ONLY on the CloudStorage Protocol.

Views receive a CloudStorage implementation via factory (DIP).
No boto3, GCS, or Azure SDK is imported here.
"""

from __future__ import annotations

import uuid

from django.http import FileResponse, HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods

from cloud_adapter.application.use_cases import (
    DeleteFileUseCase,
    DownloadFileUseCase,
    ListFilesUseCase,
    UploadFileUseCase,
)
from cloud_adapter.domain.entities import StorageKeyNotFoundError
from cloud_adapter.infrastructure.factory import SUPPORTED_PROVIDERS, make_storage
from cloud_adapter.web.models import FileUpload


@require_http_methods(["POST"])
def upload_file(request: HttpRequest) -> JsonResponse:
    """POST /files/upload?provider=s3|gcs|azure

    Accepts a multipart file upload and stores it via the chosen provider.
    Returns JSON with the upload metadata.
    """
    provider = request.GET.get("provider", "s3")
    if provider not in SUPPORTED_PROVIDERS:
        return JsonResponse(
            {"error": f"provider must be one of {SUPPORTED_PROVIDERS}"},
            status=400,
        )

    uploaded_file = request.FILES.get("file")
    if uploaded_file is None:
        return JsonResponse({"error": "No file provided in 'file' field"}, status=400)

    data = uploaded_file.read()
    key = f"{uuid.uuid4().hex}/{uploaded_file.name}"

    storage = make_storage(provider)
    result = UploadFileUseCase(storage, provider).execute(key, data)

    record = FileUpload.objects.create(
        key=result.key,
        provider=result.provider,
        size=result.size,
        url=result.url,
    )

    return JsonResponse(
        {
            "id": record.pk,
            "key": result.key,
            "provider": result.provider,
            "size": result.size,
            "url": result.url,
            "uploaded_at": record.uploaded_at.isoformat(),
        },
        status=201,
    )


@require_http_methods(["GET"])
def download_file(request: HttpRequest, file_id: int) -> HttpResponse:
    """GET /files/{id}/download

    Fetches the bytes from the cloud provider and streams them back.
    """
    try:
        record = FileUpload.objects.get(pk=file_id)
    except FileUpload.DoesNotExist:
        return JsonResponse({"error": "File record not found"}, status=404)

    storage = make_storage(record.provider)
    try:
        data = DownloadFileUseCase(storage).execute(record.key)
    except StorageKeyNotFoundError:
        return JsonResponse({"error": f"Object '{record.key}' not found in {record.provider}"}, status=404)

    filename = record.key.split("/")[-1]
    response = HttpResponse(data, content_type="application/octet-stream")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@require_http_methods(["GET"])
def list_files(request: HttpRequest) -> JsonResponse:
    """GET /files/?provider=s3|gcs|azure

    Returns all FileUpload records for the given provider.
    """
    provider = request.GET.get("provider")
    queryset = FileUpload.objects.all()
    if provider:
        if provider not in SUPPORTED_PROVIDERS:
            return JsonResponse(
                {"error": f"provider must be one of {SUPPORTED_PROVIDERS}"},
                status=400,
            )
        queryset = queryset.filter(provider=provider)

    records = [
        {
            "id": r.pk,
            "key": r.key,
            "provider": r.provider,
            "size": r.size,
            "url": r.url,
            "uploaded_at": r.uploaded_at.isoformat(),
        }
        for r in queryset
    ]
    return JsonResponse({"count": len(records), "files": records})


@require_http_methods(["DELETE"])
def delete_file(request: HttpRequest, file_id: int) -> HttpResponse:
    """DELETE /files/{id}

    Deletes the object from the cloud provider and removes the DB record.
    """
    try:
        record = FileUpload.objects.get(pk=file_id)
    except FileUpload.DoesNotExist:
        return JsonResponse({"error": "File record not found"}, status=404)

    storage = make_storage(record.provider)
    DeleteFileUseCase(storage).execute(record.key)
    record.delete()
    return HttpResponse(status=204)
