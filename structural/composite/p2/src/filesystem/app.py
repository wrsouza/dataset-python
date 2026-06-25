"""Flask application — Virtual File System (Composite over AWS S3).

Composition root: builds the S3StorageClient adapter once and injects
it into every use case. Routes are thin — all logic lives in
`application/use_cases.py` and the Composite tree in `domain/entities.py`.
"""

from __future__ import annotations

from flask import Flask, Response, jsonify, request

from filesystem.application.use_cases import (
    CalculateTotalSizeUseCase,
    CreateDirectoryUseCase,
    DeleteNodeUseCase,
    GetTreeUseCase,
    ListContentsUseCase,
    UploadFileUseCase,
)
from filesystem.domain.exceptions import FSNodeNotFoundError, FSStorageError
from filesystem.infrastructure.s3_client import S3StorageClient


def create_app(storage: S3StorageClient | None = None) -> Flask:
    """Build and configure the Flask application.

    Args:
        storage: optional pre-built S3StorageClient (used by tests to
            inject a moto-mocked client). Built lazily otherwise.
    """
    app = Flask(__name__)
    _storage = storage or S3StorageClient()

    get_tree = GetTreeUseCase(_storage)
    calculate_size = CalculateTotalSizeUseCase(_storage)
    list_contents = ListContentsUseCase(_storage)
    upload_file = UploadFileUseCase(_storage)
    create_directory = CreateDirectoryUseCase(_storage)
    delete_node = DeleteNodeUseCase(_storage)

    @app.get("/health")
    def health() -> Response:
        return jsonify({"status": "ok"})

    @app.get("/tree/<path:path>")
    def get_tree_route(path: str) -> Response:
        try:
            return jsonify(get_tree.execute(path))
        except FSNodeNotFoundError as exc:
            return Response(str(exc), status=404, mimetype="text/plain")
        except FSStorageError as exc:
            return Response(str(exc), status=502, mimetype="text/plain")

    @app.get("/size/<path:path>")
    def get_size_route(path: str) -> Response:
        try:
            return jsonify({"path": path, "size_bytes": calculate_size.execute(path)})
        except FSNodeNotFoundError as exc:
            return Response(str(exc), status=404, mimetype="text/plain")
        except FSStorageError as exc:
            return Response(str(exc), status=502, mimetype="text/plain")

    @app.get("/contents/<path:path>")
    def get_contents_route(path: str) -> Response:
        try:
            return jsonify(list_contents.execute(path))
        except FSNodeNotFoundError as exc:
            return Response(str(exc), status=404, mimetype="text/plain")
        except FSStorageError as exc:
            return Response(str(exc), status=502, mimetype="text/plain")

    @app.post("/files/<path:key>")
    def upload_file_route(key: str) -> tuple[Response, int]:
        content_type = request.content_type or "application/octet-stream"
        upload_file.execute(key, request.get_data(), content_type)
        return jsonify({"path": key, "status": "uploaded"}), 201

    @app.post("/directories/<path:path>")
    def create_directory_route(path: str) -> tuple[Response, int]:
        create_directory.execute(path)
        return jsonify({"path": path, "status": "created"}), 201

    @app.delete("/nodes/<path:path>")
    def delete_node_route(path: str) -> Response:
        try:
            delete_node.execute(path)
        except FSNodeNotFoundError as exc:
            return Response(str(exc), status=404, mimetype="text/plain")
        return jsonify({"path": path, "status": "deleted"})

    return app


def __getattr__(name: str) -> Flask:
    """Lazily build the production `app` WSGI object on first access.

    PEP 562 module-level `__getattr__`: avoids hitting S3/localstack at
    import time (which would break test collection and any tooling that
    merely imports this module), while still exposing `app` for WSGI
    servers (`flask run`, gunicorn `filesystem.app:app`).
    """
    if name == "app":
        return create_app()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
