"""RealSubject: RealDataServiceServicer.

Implements the DataService gRPC interface with plain business logic and
no awareness of rate limiting whatsoever — exactly what a hand-off team
would have written before rate limiting was ever a requirement (SRP).
"""

from __future__ import annotations

import time

from rate_limiting.infrastructure.generated import service_pb2, service_pb2_grpc

_MOCK_DATA_STORE: dict[str, str] = {
    "greeting": "hello from the real DataService",
    "version": "1.0.0",
}
_DEFAULT_VALUE = "no data found for this key"


class RealDataServiceServicer(service_pb2_grpc.DataServiceServicer):
    """RealSubject: serves data directly, with zero rate-limiting logic."""

    def GetData(
        self, request: service_pb2.DataRequest, context: object
    ) -> service_pb2.DataResponse:
        """Return the stored value for request.key, or a default placeholder."""
        value = _MOCK_DATA_STORE.get(request.key, _DEFAULT_VALUE)
        return service_pb2.DataResponse(
            key=request.key,
            value=value,
            served_at_unix_ms=int(time.time() * 1000),
        )
