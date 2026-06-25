"""Flask application factory for the Cache Decorator API.

Composition root: the only place that wires concrete dependencies
(Redis client, decorator stack) into the use case.
"""

from __future__ import annotations

import logging
import os
from dataclasses import asdict

import redis
from flask import Flask, jsonify
from flask.wrappers import Response

from cache_decorator.application.use_cases import GetProductQuoteUseCase
from cache_decorator.domain.exceptions import ProductNotFoundError
from cache_decorator.infrastructure.factory import build_data_service

logging.basicConfig(level=logging.INFO)


def create_app(redis_client: redis.Redis | None = None) -> Flask:
    """Build and configure the Flask app.

    `redis_client` can be injected (e.g. a fakeredis client in tests)
    so integration tests never need a real Redis server.
    """
    app = Flask(__name__)

    client = redis_client or redis.Redis(
        host=os.environ.get("REDIS_HOST", "localhost"),
        port=int(os.environ.get("REDIS_PORT", "6379")),
        decode_responses=True,
    )
    cache_ttl = int(os.environ.get("CACHE_TTL_SECONDS", "60"))
    retry_max_attempts = int(os.environ.get("RETRY_MAX_ATTEMPTS", "3"))
    retry_backoff_seconds = float(os.environ.get("RETRY_BACKOFF_SECONDS", "0.1"))

    data_service = build_data_service(
        redis_client=client,
        cache_ttl_seconds=cache_ttl,
        retry_max_attempts=retry_max_attempts,
        retry_backoff_seconds=retry_backoff_seconds,
    )
    get_quote = GetProductQuoteUseCase(data_service)

    @app.get("/quotes/<product_id>")
    def get_quote_route(product_id: str) -> tuple[Response, int] | Response:
        try:
            result = get_quote.execute(product_id)
        except ProductNotFoundError as exc:
            return jsonify({"error": str(exc)}), 404
        return jsonify(asdict(result))

    @app.get("/health")
    def health() -> Response:
        return jsonify({"status": "ok"})

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
