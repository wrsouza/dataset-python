"""Flask application — Image Thumbnail Cache using Flyweight pattern."""

from __future__ import annotations

import os

from flask import Flask, jsonify, request
from flask.typing import ResponseReturnValue

from thumbnails.application.use_cases import (
    GenerateThumbnailUseCase,
    GetFactoryStatsUseCase,
    GetThumbnailUseCase,
)
from thumbnails.domain.exceptions import (
    ImageNotFoundError,
    ThumbnailGenerationError,
    UnknownSpecError,
)
from thumbnails.infrastructure.factory import ThumbnailSpecFactory
from thumbnails.infrastructure.repository import InMemoryThumbnailRepository
from thumbnails.infrastructure.storage import S3ImageStorage

app = Flask(__name__)

# ── Composition root — single place where concrete deps are wired ──────────────

_S3_ENDPOINT = os.environ.get("S3_ENDPOINT_URL") or None
_S3_BUCKET = os.environ.get("S3_BUCKET", "thumbnails")

_storage = S3ImageStorage(bucket=_S3_BUCKET, endpoint_url=_S3_ENDPOINT)
_factory = ThumbnailSpecFactory()
_repository = InMemoryThumbnailRepository()


# ── Routes ─────────────────────────────────────────────────────────────────────


@app.post("/thumbnails/generate")
def generate_thumbnail() -> ResponseReturnValue:
    """Generate a thumbnail for an uploaded image using a named spec."""
    body = request.get_json(force=True) or {}
    image_key = body.get("image_key", "")
    spec_name = body.get("spec_name", "")

    if not image_key or not spec_name:
        return jsonify({"error": "image_key and spec_name are required"}), 400

    use_case = GenerateThumbnailUseCase(
        storage=_storage,
        repository=_repository,
        factory=_factory,
    )
    try:
        thumbnail = use_case.execute(image_key, spec_name)
    except UnknownSpecError as exc:
        return jsonify({"error": str(exc)}), 404
    except ImageNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except ThumbnailGenerationError as exc:
        return jsonify({"error": str(exc)}), 500

    return (
        jsonify(
            {
                "image_key": thumbnail.image_key,
                "thumbnail_key": thumbnail.thumbnail_key,
                "spec": {
                    "width": thumbnail.spec.width,
                    "height": thumbnail.spec.height,
                    "quality": thumbnail.spec.quality,
                    "format": thumbnail.spec.format,
                    "filters": list(thumbnail.spec.filters),
                },
                "flyweight_id": id(thumbnail.spec),
            }
        ),
        201,
    )


@app.get("/thumbnails/<path:image_key>/<spec_name>")
def get_thumbnail(image_key: str, spec_name: str) -> ResponseReturnValue:
    """Retrieve thumbnail metadata for an existing image+spec combination."""
    use_case = GetThumbnailUseCase(repository=_repository, factory=_factory)
    try:
        thumbnail = use_case.execute(image_key, spec_name)
    except UnknownSpecError as exc:
        return jsonify({"error": str(exc)}), 404
    except ImageNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404

    url = _storage.get_url(thumbnail.thumbnail_key)
    return (
        jsonify(
            {
                "image_key": thumbnail.image_key,
                "thumbnail_key": thumbnail.thumbnail_key,
                "url": url,
                "spec_key": thumbnail.spec.spec_key,
                "flyweight_id": id(thumbnail.spec),
            }
        ),
        200,
    )


@app.get("/specs")
def list_specs() -> ResponseReturnValue:
    """List all ThumbnailSpec flyweights registered in the factory."""
    all_specs = _factory.get_all_specs()
    return (
        jsonify(
            {
                "count": len(all_specs),
                "specs": {
                    name: {
                        "width": spec.width,
                        "height": spec.height,
                        "quality": spec.quality,
                        "format": spec.format,
                        "filters": list(spec.filters),
                        "flyweight_id": id(spec),
                    }
                    for name, spec in all_specs.items()
                },
            }
        ),
        200,
    )


@app.get("/factory/stats")
def factory_stats() -> ResponseReturnValue:
    """Show Flyweight pool stats: unique specs vs total thumbnail contexts."""
    use_case = GetFactoryStatsUseCase(factory=_factory, repository=_repository)
    stats = use_case.execute()

    # Estimate memory economy
    bytes_per_spec = 200  # intrinsic state size estimate
    bytes_per_ref = 8  # pointer size
    bytes_without = stats.total_thumbnails * bytes_per_spec
    bytes_with = (
        stats.unique_specs * bytes_per_spec + stats.total_thumbnails * bytes_per_ref
    )
    saved = max(0, bytes_without - bytes_with)
    pct = (saved / bytes_without * 100) if bytes_without > 0 else 0.0

    return (
        jsonify(
            {
                "unique_specs": stats.unique_specs,
                "total_thumbnails": stats.total_thumbnails,
                "sharing_ratio": round(stats.sharing_ratio, 2),
                "spec_names": stats.spec_names,
                "memory": {
                    "bytes_without_flyweight": bytes_without,
                    "bytes_with_flyweight": bytes_with,
                    "bytes_saved": saved,
                    "savings_percentage": round(pct, 2),
                },
                "key_insight": (
                    f"{stats.total_thumbnails} thumbnails share "
                    f"{stats.unique_specs} ThumbnailSpec objects. "
                    f"Ratio {stats.sharing_ratio:.1f}:1"
                ),
            }
        ),
        200,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
