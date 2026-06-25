"""Unit tests for AccountState.apply and the replay function."""

from __future__ import annotations

from event_sourcing.domain.entities import DomainEvent, EventType, replay


def test_replay_with_no_events_returns_closed_account_with_zero_balance() -> None:
    state = replay("acc-1", [])

    assert state.is_open is False
    assert state.balance == 0.0


def test_replay_opens_account() -> None:
    events = [DomainEvent.new("acc-1", EventType.ACCOUNT_OPENED, {})]

    state = replay("acc-1", events)

    assert state.is_open is True
    assert state.balance == 0.0


def test_replay_accumulates_deposits_and_withdrawals_in_order() -> None:
    events = [
        DomainEvent.new("acc-1", EventType.ACCOUNT_OPENED, {}),
        DomainEvent.new("acc-1", EventType.FUNDS_DEPOSITED, {"amount": 100.0}),
        DomainEvent.new("acc-1", EventType.FUNDS_WITHDRAWN, {"amount": 30.0}),
        DomainEvent.new("acc-1", EventType.FUNDS_DEPOSITED, {"amount": 5.0}),
    ]

    state = replay("acc-1", events)

    assert state.balance == 75.0
    assert state.is_open is True


def test_domain_event_new_assigns_unique_ids() -> None:
    first = DomainEvent.new("acc-1", EventType.ACCOUNT_OPENED, {})
    second = DomainEvent.new("acc-1", EventType.ACCOUNT_OPENED, {})

    assert first.event_id != second.event_id
