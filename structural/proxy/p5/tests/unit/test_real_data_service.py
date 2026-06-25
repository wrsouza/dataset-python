"""Unit tests for RealDataServiceServicer (RealSubject) in isolation."""

from __future__ import annotations

from rate_limiting.infrastructure.generated import service_pb2
from rate_limiting.infrastructure.real_data_service import RealDataServiceServicer


def test_get_data_returns_known_value(real_servicer: RealDataServiceServicer) -> None:
    request = service_pb2.DataRequest(client_id="any-client", key="greeting")

    response = real_servicer.GetData(request, context=None)

    assert response.key == "greeting"
    assert response.value == "hello from the real DataService"
    assert response.served_at_unix_ms > 0


def test_get_data_returns_default_for_unknown_key(
    real_servicer: RealDataServiceServicer,
) -> None:
    request = service_pb2.DataRequest(client_id="any-client", key="unknown")

    response = real_servicer.GetData(request, context=None)

    assert response.value == "no data found for this key"
