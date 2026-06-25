"""Proxy: RateLimitingProxyServicer — Protection Proxy implementation.

Implements the SAME gRPC interface (DataServiceServicer) as the RealSubject,
so a gRPC client connecting to the proxy's address cannot tell it apart from
talking directly to the real service (LSP). Before delegating, it asks the
EnforceRateLimitUseCase whether the call is allowed; if not, it translates
the domain RateLimitExceededError into a RESOURCE_EXHAUSTED gRPC status.

Pattern roles:
  - Subject:     DataServiceServicer / DataServiceStub (generated from .proto)
  - RealSubject: RealDataServiceServicer (infrastructure/real_data_service.py)
  - Proxy:       RateLimitingProxyServicer (this file)
"""

from __future__ import annotations

import asyncio

import grpc

from rate_limiting.application.use_cases import EnforceRateLimitUseCase
from rate_limiting.domain.entities import RateLimitConfig
from rate_limiting.domain.exceptions import RateLimitExceededError
from rate_limiting.domain.interfaces import RateLimiter
from rate_limiting.infrastructure.generated import service_pb2, service_pb2_grpc


class RateLimitingProxyServicer(service_pb2_grpc.DataServiceServicer):
    """Protection Proxy: enforces a per-client rate limit before delegating.

    Depends on the RateLimiter Protocol (DIP) and on a real_servicer that
    also implements DataServiceServicer — never on a fixed concrete class —
    so both the algorithm and the wrapped service can be swapped freely.
    """

    def __init__(
        self,
        real_servicer: service_pb2_grpc.DataServiceServicer,
        rate_limiter: RateLimiter,
        config: RateLimitConfig,
    ) -> None:
        self._real_servicer = real_servicer
        self._enforce_rate_limit = EnforceRateLimitUseCase(
            rate_limiter=rate_limiter, config=config
        )

    def GetData(
        self, request: service_pb2.DataRequest, context: grpc.ServicerContext
    ) -> service_pb2.DataResponse:
        """Check the caller's rate limit, then delegate or reject."""
        try:
            asyncio.run(self._enforce_rate_limit.execute(request.client_id))
        except RateLimitExceededError as exc:
            context.set_code(grpc.StatusCode.RESOURCE_EXHAUSTED)
            context.set_details(str(exc))
            return service_pb2.DataResponse()

        return self._real_servicer.GetData(request, context)  # type: ignore[no-any-return,no-untyped-call]
