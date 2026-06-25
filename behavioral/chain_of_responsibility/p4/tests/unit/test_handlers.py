"""Unit tests for the message processing chain handlers."""

from __future__ import annotations

from message_pipeline.domain.entities import IncomingMessage, ProcessingStatus
from message_pipeline.infrastructure.handlers import build_processing_chain


def _message(message_id: str = "m-1", **payload: object) -> IncomingMessage:
    return IncomingMessage(
        message_id=message_id, payload={"order_id": "o-1", "amount": 42, **payload}
    )


def test_valid_message_is_processed() -> None:
    chain = build_processing_chain()

    message = chain.handle(_message())

    assert message.status == ProcessingStatus.PROCESSED
    assert message.history[0].handler_name == "RoutingHandler"


def test_message_missing_required_field_is_rejected() -> None:
    chain = build_processing_chain()
    message = IncomingMessage(message_id="m-2", payload={"order_id": "o-1"})

    result = chain.handle(message)

    assert result.status == ProcessingStatus.REJECTED
    assert result.history[0].handler_name == "SchemaValidationHandler"
    assert "amount" in result.history[0].reason


def test_duplicate_message_id_is_rejected_on_second_pass() -> None:
    chain = build_processing_chain()

    first = chain.handle(_message(message_id="dup-1"))
    second = chain.handle(_message(message_id="dup-1"))

    assert first.status == ProcessingStatus.PROCESSED
    assert second.status == ProcessingStatus.REJECTED
    assert second.history[0].handler_name == "DeduplicationHandler"


def test_invalid_message_never_reaches_deduplication_check() -> None:
    chain = build_processing_chain()
    message = IncomingMessage(message_id="m-3", payload={})

    result = chain.handle(message)

    assert len(result.history) == 1
    assert result.history[0].handler_name == "SchemaValidationHandler"
