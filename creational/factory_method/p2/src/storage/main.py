"""Composition root — Flask app with storage factory routes."""
from __future__ import annotations

from flask import Flask, Response, jsonify, request

from storage.application.use_cases import (
    DeleteFileUseCase,
    DownloadFileUseCase,
    ListFilesUseCase,
    UploadFileUseCase,
)
from storage.domain.entities import (
    FileNotFoundInStorageError,
    UnsupportedProviderError,
)
from storage.infrastructure.creators import PROVIDER_REGISTRY

app = Flask(__name__)


def _get_factory(provider: str):  # type: ignore[no-untyped-def]
    factory = PROVIDER_REGISTRY.get(provider)
    if factory is None:
        raise UnsupportedProviderError(provider)
    return factory


@app.errorhandler(UnsupportedProviderError)
def handle_unsupported(exc: UnsupportedProviderError) -> tuple[Response, int]:
    return jsonify({"error": str(exc), "available": list(PROVIDER_REGISTRY.keys())}), 404


@app.errorhandler(FileNotFoundInStorageError)
def handle_not_found(exc: FileNotFoundInStorageError) -> tuple[Response, int]:
    return jsonify({"error": str(exc)}), 404


@app.post("/files/<provider>")
def upload_file(provider: str) -> tuple[Response, int]:
    """Upload a file to the given storage provider."""
    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files["file"]
    key = request.form.get("key") or (file.filename or "upload")
    data = file.read()

    factory = _get_factory(provider)
    use_case = UploadFileUseCase(factory)
    result = use_case.execute(key, data)

    return jsonify(
        {
            "key": result.key,
            "provider": result.provider,
            "url": result.url,
            "size_bytes": result.size_bytes,
        }
    ), 201


@app.get("/files/<provider>/<path:key>")
def download_file(provider: str, key: str) -> Response:
    """Download a file from the given storage provider."""
    factory = _get_factory(provider)
    use_case = DownloadFileUseCase(factory)
    data = use_case.execute(key)
    return Response(data, mimetype="application/octet-stream")


@app.delete("/files/<provider>/<path:key>")
def delete_file(provider: str, key: str) -> tuple[Response, int]:
    """Delete a file from the given storage provider."""
    factory = _get_factory(provider)
    use_case = DeleteFileUseCase(factory)
    use_case.execute(key)
    return jsonify({"deleted": True, "key": key}), 200


@app.get("/files/<provider>")
def list_files(provider: str) -> Response:
    """List all files for the given provider."""
    prefix = request.args.get("prefix", "")
    factory = _get_factory(provider)
    use_case = ListFilesUseCase(factory)
    keys = use_case.execute(prefix)
    return jsonify({"provider": provider, "keys": keys})


@app.get("/providers")
def list_providers() -> Response:
    """List all registered storage providers."""
    return jsonify(
        [{"slug": slug, "name": f.get_provider_name()} for slug, f in PROVIDER_REGISTRY.items()]
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
