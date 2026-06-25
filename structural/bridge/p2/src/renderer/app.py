"""Flask application — Renderer Bridge.

Composition root: wires Page abstractions to ContentRenderer
implementations based on the requested page type and output format.
"""

from __future__ import annotations

from flask import Flask, Response, jsonify, request

from renderer.application.use_cases import PageNotFoundError, RenderPageUseCase
from renderer.domain.interfaces import ContentRenderer
from renderer.infrastructure.implementations import (
    HTMLRenderer,
    JSONRenderer,
    XMLRenderer,
)

_RENDERERS: dict[str, ContentRenderer] = {
    "html": HTMLRenderer(),
    "json": JSONRenderer(),
    "xml": XMLRenderer(),
}
_DEFAULT_FORMAT = "json"

_use_case = RenderPageUseCase()


def create_app() -> Flask:
    """Build and configure the Flask application."""
    app = Flask(__name__)

    def _resolve_renderer(fmt: str | None) -> ContentRenderer:
        renderer = _RENDERERS.get((fmt or _DEFAULT_FORMAT).lower())
        if renderer is None:
            raise ValueError(f"Unsupported format '{fmt}'")
        return renderer

    @app.get("/health")
    def health() -> Response:
        return jsonify({"status": "ok"})

    @app.get("/products/<product_id>")
    def get_product(product_id: str) -> Response:
        try:
            renderer = _resolve_renderer(request.args.get("format"))
            body = _use_case.render_product(product_id, renderer)
        except PageNotFoundError as exc:
            return Response(str(exc), status=404, mimetype="text/plain")
        except ValueError as exc:
            return Response(str(exc), status=400, mimetype="text/plain")
        return Response(body, mimetype=renderer.content_type)

    @app.get("/blog/<slug>")
    def get_blog_post(slug: str) -> Response:
        try:
            renderer = _resolve_renderer(request.args.get("format"))
            body = _use_case.render_blog_post(slug, renderer)
        except PageNotFoundError as exc:
            return Response(str(exc), status=404, mimetype="text/plain")
        except ValueError as exc:
            return Response(str(exc), status=400, mimetype="text/plain")
        return Response(body, mimetype=renderer.content_type)

    @app.get("/users/<user_id>")
    def get_user_profile(user_id: str) -> Response:
        try:
            renderer = _resolve_renderer(request.args.get("format"))
            body = _use_case.render_user_profile(user_id, renderer)
        except PageNotFoundError as exc:
            return Response(str(exc), status=404, mimetype="text/plain")
        except ValueError as exc:
            return Response(str(exc), status=400, mimetype="text/plain")
        return Response(body, mimetype=renderer.content_type)

    return app


app = create_app()
