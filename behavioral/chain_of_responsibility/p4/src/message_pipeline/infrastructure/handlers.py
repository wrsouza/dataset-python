"""Concrete handlers ordered schema validation -> deduplication -> routing."""

from __future__ import annotations

from datetime import UTC, datetime

from message_pipeline.domain.entities import (
    IncomingMessage,
    ProcessingStatus,
    ProcessingStep,
)
from message_pipeline.domain.interfaces import MessageHandler

REQUIRED_FIELDS = frozenset({"order_id", "amount"})


class SchemaValidationHandler(MessageHandler):
    """Rejects messages whose payload is missing required fields."""

    def _inspect(self, message: IncomingMessage) -> ProcessingStep | None:
        missing = REQUIRED_FIELDS - message.payload.keys()
        if not missing:
            return None
        return ProcessingStep(
            handler_name=self.__class__.__name__,
            status=ProcessingStatus.REJECTED,
            reason=f"Missing required fields: {', '.join(sorted(missing))}",
            handled_at=datetime.now(UTC),
        )


class DeduplicationHandler(MessageHandler):
    """Rejects messages whose id has already been seen in this process."""

    def __init__(self) -> None:
        self._seen_message_ids: set[str] = set()

    def _inspect(self, message: IncomingMessage) -> ProcessingStep | None:
        if message.message_id not in self._seen_message_ids:
            self._seen_message_ids.add(message.message_id)
            return None
        return ProcessingStep(
            handler_name=self.__class__.__name__,
            status=ProcessingStatus.REJECTED,
            reason=f"Duplicate message id: {message.message_id}",
            handled_at=datetime.now(UTC),
        )


class RoutingHandler(MessageHandler):
    """Final link: marks anything that passed all prior checks as processed."""

    def _inspect(self, message: IncomingMessage) -> ProcessingStep | None:
        return ProcessingStep(
            handler_name=self.__class__.__name__,
            status=ProcessingStatus.PROCESSED,
            reason="Routed successfully after passing all checks.",
            handled_at=datetime.now(UTC),
        )


def build_processing_chain() -> MessageHandler:
    """Wire the default schema-validation -> deduplication -> routing chain."""
    schema_handler = SchemaValidationHandler()
    dedup_handler = DeduplicationHandler()
    routing_handler = RoutingHandler()
    schema_handler.set_next(dedup_handler).set_next(routing_handler)
    return schema_handler
