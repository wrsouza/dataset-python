"""Core entities for the event-sourced account domain."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum


class EventType(StrEnum):
    """The kinds of domain events an account can emit."""

    ACCOUNT_OPENED = "account_opened"
    FUNDS_DEPOSITED = "funds_deposited"
    FUNDS_WITHDRAWN = "funds_withdrawn"


@dataclass(frozen=True)
class DomainEvent:
    """An immutable fact that happened to an account, the unit of the event log."""

    event_id: str
    account_id: str
    event_type: EventType
    payload: dict[str, object]
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @staticmethod
    def new(
        account_id: str, event_type: EventType, payload: dict[str, object]
    ) -> DomainEvent:
        """Build a new event with a fresh id and the current timestamp."""
        return DomainEvent(
            event_id=str(uuid.uuid4()),
            account_id=account_id,
            event_type=event_type,
            payload=payload,
        )


@dataclass
class AccountState:
    """The current materialised state of an account, derived by replaying events.

    This is the Receiver in the Command pattern: commands validate
    themselves against this state, but only events ever change it.
    """

    account_id: str
    balance: float = 0.0
    is_open: bool = False

    def apply(self, event: DomainEvent) -> AccountState:
        """Return a new AccountState reflecting `event` being applied."""
        if event.event_type == EventType.ACCOUNT_OPENED:
            return AccountState(account_id=self.account_id, balance=0.0, is_open=True)
        if event.event_type == EventType.FUNDS_DEPOSITED:
            amount = float(str(event.payload["amount"]))
            return AccountState(
                account_id=self.account_id,
                balance=self.balance + amount,
                is_open=self.is_open,
            )
        if event.event_type == EventType.FUNDS_WITHDRAWN:
            amount = float(str(event.payload["amount"]))
            return AccountState(
                account_id=self.account_id,
                balance=self.balance - amount,
                is_open=self.is_open,
            )
        return self


def replay(account_id: str, events: list[DomainEvent]) -> AccountState:
    """Rebuild an account's current state by folding its full event history."""
    state = AccountState(account_id=account_id)
    for event in events:
        state = state.apply(event)
    return state
