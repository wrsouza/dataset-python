"""Domain-level exceptions for the Rate Limiting Proxy project."""

from __future__ import annotations


class RateLimitExceededError(Exception):
    """Raised by the application layer when a client exhausts its budget.

    The infrastructure layer (RateLimitingProxyServicer) catches this and
    translates it into a gRPC RESOURCE_EXHAUSTED status — the domain and
    application layers stay free of any gRPC-specific vocabulary.
    """

    def __init__(self, client_id: str, retry_after_seconds: float) -> None:
        self.client_id = client_id
        self.retry_after_seconds = retry_after_seconds
        super().__init__(
            f"Client '{client_id}' exceeded its rate limit; "
            f"retry after {retry_after_seconds:.2f}s"
        )
