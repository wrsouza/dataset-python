"""Example client — connects to the proxy's address exactly like it would
connect to the real DataService. It is unaware that a Protection Proxy
intercepts every call to enforce rate limiting.
"""

from __future__ import annotations

import os

import grpc

from rate_limiting.infrastructure.generated import service_pb2, service_pb2_grpc

_DEFAULT_TARGET = "localhost:50051"


def main() -> None:
    target = os.environ.get("GRPC_TARGET", _DEFAULT_TARGET)
    client_id = os.environ.get("CLIENT_ID", "demo-client")

    with grpc.insecure_channel(target) as channel:
        stub = service_pb2_grpc.DataServiceStub(channel)  # type: ignore[no-untyped-call]
        for attempt in range(1, 8):
            request = service_pb2.DataRequest(client_id=client_id, key="greeting")
            try:
                response = stub.GetData(request)
                print(f"[{attempt}] OK -> {response.value}")
            except grpc.RpcError as exc:
                print(f"[{attempt}] {exc.code()} -> {exc.details()}")


if __name__ == "__main__":
    main()
