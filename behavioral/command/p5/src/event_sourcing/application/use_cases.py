"""Use cases orchestrating command validation, event persistence, and replay."""

from __future__ import annotations

from event_sourcing.domain.entities import AccountState, DomainEvent, replay
from event_sourcing.domain.interfaces import AccountCommand, EventPublisher, EventStore


class DispatchCommandUseCase:
    """Validates a command against the replayed state, then persists and publishes."""

    def __init__(self, event_store: EventStore, publisher: EventPublisher) -> None:
        self._event_store = event_store
        self._publisher = publisher

    def execute(self, account_id: str, command: AccountCommand) -> DomainEvent:
        existing_events = self._event_store.get_events(account_id)
        current_state = replay(account_id, existing_events)

        event = command.execute(current_state)

        self._event_store.append(event)
        self._publisher.publish(event)
        return event


class GetAccountStateUseCase:
    """Returns an account's current state, rebuilt by replaying its events."""

    def __init__(self, event_store: EventStore) -> None:
        self._event_store = event_store

    def execute(self, account_id: str) -> AccountState:
        events = self._event_store.get_events(account_id)
        return replay(account_id, events)


class GetEventHistoryUseCase:
    """Returns the full, ordered event history for an account."""

    def __init__(self, event_store: EventStore) -> None:
        self._event_store = event_store

    def execute(self, account_id: str) -> list[DomainEvent]:
        return self._event_store.get_events(account_id)
