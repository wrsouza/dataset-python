"""Flask application factory for the API Cache Proxy demo."""

from __future__ import annotations

import dataclasses
import logging
import os

import redis
from flask import Flask, jsonify
from flask.typing import ResponseReturnValue

from cache_proxy.application.use_cases import (
    FlushCacheUseCase,
    GetCacheStatsUseCase,
    GetExchangeRateUseCase,
    GetStockPriceUseCase,
    GetWeatherUseCase,
)
from cache_proxy.infrastructure.proxy import RedisCacheProxy
from cache_proxy.infrastructure.real_subject import MockExternalAPIService

logging.basicConfig(level=logging.DEBUG)


def create_app() -> Flask:
    """Application factory — wires up DI and registers routes."""
    app = Flask(__name__)

    # --- Composition root (the only place with concrete dependencies) --------
    redis_client = redis.Redis(
        host=os.environ.get("REDIS_HOST", "localhost"),
        port=int(os.environ.get("REDIS_PORT", "6379")),
        password=os.environ.get("REDIS_PASSWORD", None) or None,
        decode_responses=True,
    )
    real_service = MockExternalAPIService()
    proxy = RedisCacheProxy(wrapped=real_service, redis_client=redis_client)

    # Use cases injected with abstractions (DIP)
    get_weather = GetWeatherUseCase(proxy)
    get_exchange = GetExchangeRateUseCase(proxy)
    get_stock = GetStockPriceUseCase(proxy)
    get_stats = GetCacheStatsUseCase(proxy)
    flush_cache = FlushCacheUseCase(proxy)

    # --- Routes --------------------------------------------------------------

    @app.get("/weather/<city>")
    def weather(city: str) -> ResponseReturnValue:
        data = get_weather.execute(city)
        return jsonify(dataclasses.asdict(data))

    @app.get("/exchange/<from_cur>/<to_cur>")
    def exchange(from_cur: str, to_cur: str) -> ResponseReturnValue:
        rate = get_exchange.execute(from_cur, to_cur)
        return jsonify({"from": from_cur.upper(), "to": to_cur.upper(), "rate": rate})

    @app.get("/stocks/<ticker>")
    def stocks(ticker: str) -> ResponseReturnValue:
        data = get_stock.execute(ticker)
        return jsonify(dataclasses.asdict(data))

    @app.get("/cache/stats")
    def cache_stats() -> ResponseReturnValue:
        stats = get_stats.execute()
        return jsonify(
            {
                "hits": stats.hits,
                "misses": stats.misses,
                "total": stats.total,
                "hit_rate": round(stats.hit_rate, 4),
            }
        )

    @app.delete("/cache/flush")
    def cache_flush() -> ResponseReturnValue:
        removed = flush_cache.execute()
        return jsonify({"keys_removed": removed})

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
