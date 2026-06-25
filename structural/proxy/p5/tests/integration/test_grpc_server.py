"""Integration test: a real grpc.server running in a background thread,
talked to by a real grpc.Channel — exercising the full path
client -> channel -> RateLimitingProxyServicer -> RealDataServiceServicer,
with Redis replaced by fakeredis so no external service is required.
"""

from __future__ import annotations

from collections.abc import Iterator
from concurrent import futures

import grpc
import pytest
from fakeredis import aioredis as fake_aioredis

from rate_limiting.domain.entities import RateLimitConfig
from rate_limiting.infrastructure.generated import service_pb2, service_pb2_grpc
from rate_limiting.infrastructure.rate_limiting_proxy import RateLimitingProxyServicer
from rate_limiting.infrastructure.real_data_service import RealDataServiceServicer
from rate_limiting.infrastructure.token_bucket_rate_limiter import (
    TokenBucketRateLimiter,
)

_TEST_MAX_REQUESTS = 2
_TEST_WINDOW_SECONDS = 10
_TEST_PORT = 0  # let the OS pick a free port


@pytest.fixture
def grpc_server_address() -> Iterator[str]:
    redis_client = fake_aioredis.FakeRedis()
    config = RateLimitConfig(
        max_requests=_TEST_MAX_REQUESTS, window_seconds=_TEST_WINDOW_SECONDS
    )
    proxy_servicer = RateLimitingProxyServicer(
        real_servicer=RealDataServiceServicer(),
        rate_limiter=TokenBucketRateLimiter(redis_client=redis_client),
        config=config,
    )

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    service_pb2_grpc.add_DataServiceServicer_to_server(proxy_servicer, server)
    port = server.add_insecure_port(f"[::]:{_TEST_PORT}")
    server.start()

    yield f"localhost:{port}"

    server.stop(grace=None)


def test_calls_within_budget_are_delegated_successfully(
    grpc_server_address: str,
) -> None:
    with grpc.insecure_channel(grpc_server_address) as channel:
        stub = service_pb2_grpc.DataServiceStub(channel)
        request = service_pb2.DataRequest(client_id="integration-client", key="version")

        response = stub.GetData(request)

        assert response.value == "1.0.0"


def test_calls_beyond_budget_return_resource_exhausted(
    grpc_server_address: str,
) -> None:
    with grpc.insecure_channel(grpc_server_address) as channel:
        stub = service_pb2_grpc.DataServiceStub(channel)
        request = service_pb2.DataRequest(
            client_id="integration-client-2", key="greeting"
        )

        for _ in range(_TEST_MAX_REQUESTS):
            stub.GetData(request)

        with pytest.raises(grpc.RpcError) as exc_info:
            stub.GetData(request)

        assert exc_info.value.code() == grpc.StatusCode.RESOURCE_EXHAUSTED


def test_different_clients_have_independent_budgets(
    grpc_server_address: str,
) -> None:
    with grpc.insecure_channel(grpc_server_address) as channel:
        stub = service_pb2_grpc.DataServiceStub(channel)

        for _ in range(_TEST_MAX_REQUESTS):
            stub.GetData(service_pb2.DataRequest(client_id="client-X", key="greeting"))

        response = stub.GetData(
            service_pb2.DataRequest(client_id="client-Y", key="greeting")
        )

        assert response.value == "hello from the real DataService"
