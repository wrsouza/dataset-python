"""Unit tests for the dispatch/get-state/get-history use cases."""

from __future__ import annotations

import pytest

from event_sourcing.application.use_cases import (
    DispatchCommandUseCase,
    GetAccountStateUseCase,
    GetEventHistoryUseCase,
)
from event_sourcing.domain.entities import DomainEvent
from event_sourcing.domain.exceptions import AccountNotOpenError
from event_sourcing.domain.interfaces import EventPublisher, EventStore
from event_sourcing.infrastructure.commands import (
    DepositCommand,
    OpenAccountCommand,
    WithdrawCommand,
)


class InMemoryEventStore(EventStore):
    def __init__(self) -> None:
        self._events: dict[str, list[DomainEvent]] = {}

    def append(self, event: DomainEvent) -> None:
        self._events.setdefault(event.account_id, []).append(event)

    def get_events(self, account_id: str) -> list[DomainEvent]:
        return list(self._events.get(account_id, []))


class FakeEventPublisher(EventPublisher):
    def __init__(self) -> None:
        self.published: list[DomainEvent] = []

    def publish(self, event: DomainEvent) -> None:
        self.published.append(event)


def test_dispatch_open_account_persists_and_publishes() -> None:
    store = InMemoryEventStore()
    publisher = FakeEventPublisher()
    use_case = DispatchCommandUseCase(store, publisher)

    event = use_case.execute("acc-1", OpenAccountCommand())

    assert store.get_events("acc-1") == [event]
    assert publisher.published == [event]


def test_dispatch_propagates_domain_errors_without_persisting() -> None:
    store = InMemoryEventStore()
    publisher = FakeEventPublisher()
    use_case = DispatchCommandUseCase(store, publisher)

    with pytest.raises(AccountNotOpenError):
        use_case.execute("acc-1", DepositCommand(10.0))

    assert store.get_events("acc-1") == []
    assert publisher.published == []


def test_full_workflow_open_deposit_withdraw() -> None:
    store = InMemoryEventStore()
    publisher = FakeEventPublisher()
    dispatch = DispatchCommandUseCase(store, publisher)

    dispatch.execute("acc-1", OpenAccountCommand())
    dispatch.execute("acc-1", DepositCommand(100.0))
    dispatch.execute("acc-1", WithdrawCommand(40.0))

    state = GetAccountStateUseCase(store).execute("acc-1")
    assert state.balance == 60.0
    assert state.is_open is True

    history = GetEventHistoryUseCase(store).execute("acc-1")
    assert len(history) == 3


def test_get_account_state_for_unknown_account_returns_closed_zero_balance() -> None:
    state = GetAccountStateUseCase(InMemoryEventStore()).execute("ghost")

    assert state.is_open is False
    assert state.balance == 0.0
