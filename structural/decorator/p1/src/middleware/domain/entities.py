"""Domain entities for the HTTP Middleware Pipeline."""

from __future__ import annotations

import gzip
import time
import uuid
from dataclasses import dataclass, field


@dataclass
class ConcreteHTTPRequest:
    """Concrete HTTP request entity."""

    method: str
    path: str
    headers: dict[str, str] = field(default_factory=dict)
    body: bytes = b""
    query_params: dict[str, str] = field(default_factory=dict)
    client_ip: str = "127.0.0.1"
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)


@dataclass
class ConcreteHTTPResponse:
    """Concrete HTTP response entity."""

    status_code: int
    headers: dict[str, str] = field(default_factory=dict)
    body: bytes = b""
    processing_time_ms: float = 0.0

    def compress_body(self) -> None:
        """Compress body with gzip in-place."""
        self.body = gzip.compress(self.body)
        self.headers["Content-Encoding"] = "gzip"
        self.headers["Content-Length"] = str(len(self.body))


@dataclass
class AuthToken:
    """Parsed JWT payload."""

    user_id: str
    roles: list[str]
    expires_at: float


class AuthenticationError(Exception):
    """Raised when JWT is missing or invalid."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Authentication failed: {reason}")


class RateLimitExceededError(Exception):
    """Raised when a client exceeds the allowed request rate."""

    def __init__(self, client_ip: str, limit: int) -> None:
        self.client_ip = client_ip
        self.limit = limit
        super().__init__(f"Rate limit {limit}/min exceeded for {client_ip}")
