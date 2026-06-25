"""Use case that assembles and runs the request validation chain."""

from __future__ import annotations

from validation.domain.entities import APIRequest, APIResponse
from validation.domain.interfaces import RequestHandler

DEFAULT_SUCCESS_MESSAGE = "Request passed all validation handlers"


class ValidateRequestUseCase:
    """Builds the Chain of Responsibility and submits requests to it.

    SRP: the only responsibility is orchestrating the chain execution;
    each handler keeps its own validation logic.
    DIP: receives the chain's entry point (an abstraction, ``RequestHandler``)
    via constructor injection instead of constructing concrete handlers itself.
    OCP: handlers can be reordered, added, or removed by the caller that
    builds the chain — this use case never changes when handlers change.
    """

    def __init__(self, entry_handler: RequestHandler) -> None:
        self._entry_handler = entry_handler

    def execute(self, request: APIRequest) -> APIResponse:
        """Run the request through the chain, returning the final outcome."""
        result = self._entry_handler.handle(request)
        if result is not None:
            return result
        return APIResponse.ok(message=DEFAULT_SUCCESS_MESSAGE)


def build_default_chain(*handlers: RequestHandler) -> RequestHandler:
    """Link handlers in the given order and return the chain's entry point.

    Centralizing the linking logic in one factory function means adding a
    new handler to the pipeline only requires passing it here — no existing
    handler implementation needs to change (Open/Closed in practice).
    """
    if not handlers:
        raise ValueError("At least one handler is required to build a chain")

    for current, following in zip(handlers, handlers[1:], strict=False):
        current.set_next(following)

    return handlers[0]
