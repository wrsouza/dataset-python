"""Flask application factory for the S3 Bucket Iterator API.

Composition root: the only place that wires the concrete boto3 S3
source into the use cases.
"""

from __future__ import annotations

from flask import Flask, jsonify, request
from flask.wrappers import Response

from s3_iterator.application.use_cases import (
    ListObjectsPageUseCase,
    SummarizeBucketUseCase,
)
from s3_iterator.domain.entities import S3Object
from s3_iterator.domain.interfaces import S3ObjectSource
from s3_iterator.infrastructure.factory import build_source


def _object_to_dict(obj: S3Object) -> dict[str, object]:
    return {
        "key": obj.key,
        "size": obj.size,
        "last_modified": obj.last_modified.isoformat(),
    }


def create_app(source: S3ObjectSource | None = None) -> Flask:
    """Build and configure the Flask app.

    `source` can be injected (e.g. a moto-backed source in tests) so
    integration tests never need a real S3 bucket.
    """
    app = Flask(__name__)

    object_source = source or build_source()
    list_objects = ListObjectsPageUseCase(object_source)
    summarize = SummarizeBucketUseCase(object_source)

    @app.get("/objects")
    def list_objects_route() -> Response:
        token = request.args.get("continuation_token")
        limit = int(request.args.get("limit", "1000"))
        page = list_objects.execute(token, limit)
        return jsonify(
            {
                "items": [_object_to_dict(obj) for obj in page.items],
                "next_token": page.next_token,
            }
        )

    @app.get("/objects/summary")
    def summary_route() -> Response:
        summary = summarize.execute()
        return jsonify(
            {
                "object_count": summary.object_count,
                "total_size_bytes": summary.total_size_bytes,
            }
        )

    @app.get("/health")
    def health() -> Response:
        return jsonify({"status": "ok"})

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=False)
