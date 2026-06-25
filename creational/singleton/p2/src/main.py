"""Flask application entry point for P2 — Cache Manager.

Demonstrates:
- CacheManager Singleton shared by all request handlers.
- @cached decorator that transparently caches endpoint responses.
- before_request / after_request hooks for logging.
- Circuit breaker state exposed via /cache/stats.
"""

from __future__ import annotations

import functools
import json
import os
import time
from collections.abc import Callable
from typing import Any

from flask import Flask, Response, jsonify, request

from cache.application.use_cases import (
    FlushCacheUseCase,
    GetCacheStatsUseCase,
    GetProductsUseCase,
)
from cache.infrastructure.singleton import CacheManager

app = Flask(__name__)

# ── Bootstrap the Singleton ────────────────────────────────────────────────
# Called once at startup; subsequent CacheManager() calls return the same object.
_cache = CacheManager()
_cache.configure(
    host=os.environ.get("REDIS_HOST", "redis"),
    port=int(os.environ.get("REDIS_PORT", "6379")),
    password=os.environ.get("REDIS_PASSWORD", ""),
)


# ── @cached decorator ──────────────────────────────────────────────────────


def cached(ttl: int = 60) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Route decorator that caches the JSON response for `ttl` seconds.

    OCP: adding caching to a new endpoint requires only decorating it —
    no changes to CacheManager.
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            cache = CacheManager()  # always the same singleton
            cache_key = f"route:{request.path}:{request.query_string.decode()}"
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                response = jsonify(cached_value)
                response.headers["X-Cache"] = "HIT"
                response.headers["X-Singleton-Id"] = str(id(cache))
                return response

            result = fn(*args, **kwargs)
            if isinstance(result, Response):
                data = json.loads(result.get_data())
            else:
                data = result
            cache.set(cache_key, data, ttl=ttl)
            response = jsonify(data)
            response.headers["X-Cache"] = "MISS"
            response.headers["X-Singleton-Id"] = str(id(cache))
            return response

        return wrapper

    return decorator


# ── Hooks ─────────────────────────────────────────────────────────────────


@app.before_request
def record_start_time() -> None:
    request._start = time.monotonic()  # type: ignore[attr-defined]


@app.after_request
def add_timing_header(response: Response) -> Response:
    elapsed = time.monotonic() - getattr(request, "_start", time.monotonic())
    response.headers["X-Response-Time"] = f"{elapsed * 1000:.2f}ms"
    return response


# ── Routes ────────────────────────────────────────────────────────────────


@app.get("/products")
@cached(ttl=60)
def list_products() -> Any:
    """Return products. First request hits the 'DB'; subsequent hits read cache."""
    cache = CacheManager()
    return GetProductsUseCase(cache).execute()


@app.post("/cache/flush")
def flush_cache() -> Any:
    """Evict all cached keys."""
    cache = CacheManager()
    ok = FlushCacheUseCase(cache).execute()
    return jsonify({"flushed": ok, "singleton_id": id(cache)})


@app.get("/cache/stats")
def cache_stats() -> Any:
    """Return cache statistics and circuit breaker state."""
    cache = CacheManager()
    stats = GetCacheStatsUseCase(cache).execute()
    return jsonify(
        {
            "singleton_id": id(cache),
            **stats.to_dict(),
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
