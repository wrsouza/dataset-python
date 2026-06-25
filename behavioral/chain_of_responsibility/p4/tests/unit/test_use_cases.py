"""Unit tests for the process/consume-and-process use cases."""

from __future__ import annotations

from message_pipeline.application.use_cases import (
    ConsumeAndProcessUseCase,
    ProcessMessageUseCase,
)
from message_pipeline.domain.entities import IncomingMessage, ProcessingStatus
from message_pipeline.infrastructure.handlers import build_processing_chain
from message_pipeline.infrastructure.rabbitmq_consumer import RabbitMQQueueConsumer
from tests.unit.test_rabbitmq_consumer import FakeChannel


def test_process_message_use_case_runs_chain() -> None:
    chain = build_processing_chain()
    use_case = ProcessMessageUseCase(chain)

    result = use_case.execute(
        IncomingMessage(message_id="m-1", payload={"order_id": "o-1", "amount": 1})
    )

    assert result.status == ProcessingStatus.PROCESSED


def test_consume_and_process_use_case_acks_processed_messages() -> None:
    channel = FakeChannel([{"message_id": "m-1", "order_id": "o-1", "amount": 10}])
    consumer = RabbitMQQueueConsumer(channel)
    chain = build_processing_chain()
    use_case = ConsumeAndProcessUseCase(consumer, chain)

    result = use_case.execute("orders", limit=1)

    assert len(result.messages) == 1
    assert result.messages[0].status == ProcessingStatus.PROCESSED
    assert channel.acked_tags == [1]


def test_consume_and_process_use_case_with_no_messages() -> None:
    consumer = RabbitMQQueueConsumer(FakeChannel([]))
    chain = build_processing_chain()
    use_case = ConsumeAndProcessUseCase(consumer, chain)

    result = use_case.execute("orders", limit=5)

    assert result.messages == []
