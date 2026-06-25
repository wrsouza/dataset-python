"""Unit tests for DrainAvailableMessagesUseCase and SummarizeAvailableMessagesUseCase.

Two use cases: one drains the stream, the other also aggregates totals.
"""

from __future__ import annotations

from stream_iterator.application.use_cases import (
    DrainAvailableMessagesUseCase,
    SummarizeAvailableMessagesUseCase,
)
from stream_iterator.domain.entities import StreamMessage
from tests.unit.test_stream_iterator import FakeMessageSource


def test_drain_yields_every_message_in_the_batch() -> None:
    batch = [
        StreamMessage(key="a", value={"amount": 1}, offset=0, partition=0),
        StreamMessage(key="b", value={"amount": 2}, offset=1, partition=0),
    ]
    source = FakeMessageSource([batch])
    use_case = DrainAvailableMessagesUseCase(source)

    drained = list(use_case.execute())

    assert [m.key for m in drained] == ["a", "b"]


def test_drain_with_nothing_available_yields_nothing() -> None:
    source = FakeMessageSource([[]])
    use_case = DrainAvailableMessagesUseCase(source)

    assert list(use_case.execute()) == []


def test_summarize_sums_amount_field_and_counts_messages() -> None:
    batch = [
        StreamMessage(key="a", value={"amount": 10.5}, offset=0, partition=0),
        StreamMessage(key="b", value={"amount": 4.5}, offset=1, partition=0),
    ]
    source = FakeMessageSource([batch])
    use_case = SummarizeAvailableMessagesUseCase(source)

    summary, messages = use_case.execute()

    assert summary.message_count == 2
    assert summary.total_amount == 15.0
    assert len(messages) == 2


def test_summarize_ignores_messages_without_numeric_amount() -> None:
    batch = [StreamMessage(key="a", value={"note": "no amount"}, offset=0, partition=0)]
    source = FakeMessageSource([batch])
    use_case = SummarizeAvailableMessagesUseCase(source)

    summary, _ = use_case.execute()

    assert summary.message_count == 1
    assert summary.total_amount == 0.0


def test_summarize_with_nothing_available_returns_zeroes() -> None:
    source = FakeMessageSource([[]])
    use_case = SummarizeAvailableMessagesUseCase(source)

    summary, messages = use_case.execute()

    assert summary.message_count == 0
    assert summary.total_amount == 0.0
    assert messages == []
