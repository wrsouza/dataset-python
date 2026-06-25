"""Abstractions for the Command pattern and the event store/publisher boundaries."""

from __future__ import annotations

from abc import ABC, abstractmethod

from event_sourcing.domain.entities import AccountState, DomainEvent


class AccountCommand(ABC):
    """Encapsulates a single intent to change an account's state.

    A command never mutates state directly — it validates itself against
    the current `AccountState` and, if valid, returns the `DomainEvent`
    that represents what happened. The event (not the command) is what
    gets persisted and replayed.
    """

    @abstractmethod
    def execute(self, state: AccountState) -> DomainEvent:
        """Validate against `state` and return the resulting DomainEvent."""


class EventStore(ABC):
    """Append-only persistence boundary for domain events."""

    @abstractmethod
    def append(self, event: DomainEvent) -> None:
        """Persist a new event."""

    @abstractmethod
    def get_events(self, account_id: str) -> list[DomainEvent]:
        """Return every event for an account, ordered from oldest to newest."""


class EventPublisher(ABC):
    """Boundary for publishing a domain event to a message broker."""

    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        """Publish an event for downstream consumers."""
