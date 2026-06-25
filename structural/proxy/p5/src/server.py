"""gRPC server composition root — Rate Limiting Proxy (Protection Proxy).

Wires RealDataServiceServicer (RealSubject) behind RateLimitingProxyServicer
(Proxy) and registers ONLY the proxy with the gRPC server. Clients connect
to this server's address and talk to DataService normally; they never see
RealDataServiceServicer directly and have no way to bypass the proxy.
"""

from __future__ import annotations

import os
import time
from concurrent import futures

import grpc
import redis.asyncio as redis

from rate_limiting.domain.entities import RateLimitConfig
from rate_limiting.infrastructure.generated import service_pb2_grpc
from rate_limiting.infrastructure.rate_limiting_proxy import RateLimitingProxyServicer
from rate_limiting.infrastructure.real_data_service import RealDataServiceServicer
from rate_limiting.infrastructure.token_bucket_rate_limiter import (
    TokenBucketRateLimiter,
)

_DEFAULT_GRPC_PORT = "50051"
_DEFAULT_REDIS_URL = "redis://localhost:6379/0"
_DEFAULT_MAX_REQUESTS = 5
_DEFAULT_WINDOW_SECONDS = 10
_THREAD_POOL_WORKERS = 10


def _build_rate_limit_config() -> RateLimitConfig:
    return RateLimitConfig(
        max_requests=int(
            os.environ.get("RATE_LIMIT_MAX_REQUESTS", _DEFAULT_MAX_REQUESTS)
        ),
        window_seconds=int(
            os.environ.get("RATE_LIMIT_WINDOW_SECONDS", _DEFAULT_WINDOW_SECONDS)
        ),
    )


def create_server() -> grpc.Server:
    """Build and return a fully-wired, but not-yet-started, gRPC server."""
    redis_url = os.environ.get("REDIS_URL", _DEFAULT_REDIS_URL)
    redis_client = redis.from_url(redis_url)

    real_servicer = RealDataServiceServicer()
    rate_limiter = TokenBucketRateLimiter(redis_client=redis_client)
    config = _build_rate_limit_config()

    proxy_servicer = RateLimitingProxyServicer(
        real_servicer=real_servicer, rate_limiter=rate_limiter, config=config
    )

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=_THREAD_POOL_WORKERS))
    service_pb2_grpc.add_DataServiceServicer_to_server(  # type: ignore[no-untyped-call]
        proxy_servicer, server
    )
    return server


def serve() -> None:
    """Start the gRPC server and block until terminated."""
    port = os.environ.get("GRPC_PORT", _DEFAULT_GRPC_PORT)
    server = create_server()
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"RateLimitingProxyServicer listening on port {port}")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(grace=5)


if __name__ == "__main__":
    serve()
