"""FastAPI application entry point for the Cloud Storage Factory API.

Composition root: the only module that resolves concrete factories.
All use cases receive the CloudStorageFactory abstraction.
"""
from __future__ import annotations

import os

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import Response

from cloud_storage.application.use_cases import (
    DeleteFileUseCase,
    DownloadFileUseCase,
    GetMetadataUseCase,
    GetSignedUrlUseCase,
    UploadFileUseCase,
)
from cloud_storage.domain.entities import ObjectNotFoundError
from cloud_storage.infrastructure.factories import build_factory_for_provider

app = FastAPI(
    title="Cloud Storage Factory",
    description="Abstract Factory pattern — multi-provider cloud storage API",
    version="0.1.0",
)

LOCALSTACK_URL = os.environ.get("LOCALSTACK_URL", "http://localstack:4566")


def _get_factory(provider: str):  # type: ignore[no-untyped-def]
    """Resolve the ConcreteFactory for the given provider (composition root)."""
    try:
        return build_factory_for_provider(provider, localstack_url=LOCALSTACK_URL)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/upload")
async def upload_file(
    provider: str = Query(default="aws", description="Cloud provider: aws | gcs | azure"),
    key: str = Query(..., description="Object key / path"),
    file: UploadFile = File(...),
) -> dict[str, object]:
    """Upload a file to the specified cloud provider."""
    data = await file.read()
    content_type = file.content_type or "application/octet-stream"
    factory = _get_factory(provider)
    use_case = UploadFileUseCase(factory=factory)
    result = use_case.execute(key=key, data=data, content_type=content_type)
    return result.to_dict()


@app.get("/download/{key:path}")
def download_file(
    key: str,
    provider: str = Query(default="aws"),
) -> Response:
    """Download a file from the specified cloud provider."""
    factory = _get_factory(provider)
    use_case = DownloadFileUseCase(factory=factory)
    try:
        data = use_case.execute(key=key)
    except ObjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return Response(content=data, media_type="application/octet-stream")


@app.delete("/{key:path}")
def delete_file(
    key: str,
    provider: str = Query(default="aws"),
) -> dict[str, str]:
    """Delete a file from the specified cloud provider."""
    factory = _get_factory(provider)
    use_case = DeleteFileUseCase(factory=factory)
    use_case.execute(key=key)
    return {"status": "deleted", "key": key, "provider": provider}


@app.get("/signed-url/{key:path}")
def get_signed_url(
    key: str,
    provider: str = Query(default="aws"),
    expires_in: int = Query(default=3600, ge=1, le=86400),
) -> dict[str, object]:
    """Generate a time-limited signed URL for accessing an object."""
    factory = _get_factory(provider)
    use_case = GetSignedUrlUseCase(factory=factory)
    result = use_case.execute(key=key, expires_in_seconds=expires_in)
    return result.to_dict()


@app.get("/metadata/{key:path}")
def get_metadata(
    key: str,
    provider: str = Query(default="aws"),
) -> dict[str, object]:
    """Retrieve metadata for a stored object."""
    factory = _get_factory(provider)
    use_case = GetMetadataUseCase(factory=factory)
    try:
        result = use_case.execute(key=key)
    except ObjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return result.to_dict()


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "service": "cloud-storage-factory"}
