"""Handler ABC for request validation chain."""

from __future__ import annotations

from abc import ABC, abstractmethod

from validation.domain.entities import APIRequest, APIResponse


class RequestHandler(ABC):
    """Abstract base for all request validation handlers.

    Implements the Chain of Responsibility pattern:
    each handler either processes the request or passes it to the next.
    """

    def __init__(self) -> None:
        self._next_handler: RequestHandler | None = None

    def set_next(self, handler: RequestHandler) -> RequestHandler:
        """Link the next handler and return it for fluent chaining."""
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, request: APIRequest) -> APIResponse | None:
        """Process the request or delegate to the next handler.

        Returns APIResponse if this handler short-circuits the chain,
        or None to continue to the next handler.
        """

    def _pass_to_next(self, request: APIRequest) -> APIResponse | None:
        """Delegate to the next handler if one exists."""
        if self._next_handler is not None:
            return self._next_handler.handle(request)
        return None
