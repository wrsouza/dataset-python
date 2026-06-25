"""Domain interfaces for the HTTP Middleware Pipeline.

Defines the Component ABC and Decorator ABC following the GoF Decorator pattern.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol


class HTTPRequest(Protocol):
    """Minimal HTTP request contract."""

    method: str
    path: str
    headers: dict[str, str]
    body: bytes
    query_params: dict[str, str]
    client_ip: str


class HTTPResponse(Protocol):
    """Minimal HTTP response contract."""

    status_code: int
    headers: dict[str, str]
    body: bytes


class RequestHandler(ABC):
    """Component ABC — the interface for all handlers and decorators.

    Every concrete handler and every decorator must implement `handle`.
    This is the core role in the GoF Decorator pattern.
    """

    @abstractmethod
    def handle(self, request: "ConcreteHTTPRequest") -> "ConcreteHTTPResponse":
        """Process the request and return a response."""
        ...


class RequestHandlerDecorator(RequestHandler):
    """Decorator ABC — wraps a RequestHandler and delegates to it.

    Subclasses add behaviour before/after calling `self._wrapped.handle(request)`.
    Following OCP: new middleware = new subclass, existing code untouched.
    """

    def __init__(self, wrapped: RequestHandler) -> None:
        self._wrapped = wrapped

    def handle(self, request: "ConcreteHTTPRequest") -> "ConcreteHTTPResponse":
        """Default delegation — subclasses override to inject behaviour."""
        return self._wrapped.handle(request)


# Forward-reference types used in type hints above
from middleware.domain.entities import ConcreteHTTPRequest, ConcreteHTTPResponse  # noqa: E402, F401
