"""Abstractions for the Mediator pattern: EventBus and EventHandler."""

from __future__ import annotations

from abc import ABC, abstractmethod

from event_bus.domain.entities import Event


class EventHandler(ABC):
    """A Colleague: reacts to events of a given type, without knowing who

    published them or who else is also listening.
    """

    @abstractmethod
    def get_handler_id(self) -> str:
        """Return this handler's stable identifier."""

    @abstractmethod
    def handle(self, event: Event) -> None:
        """React to an event routed by the bus to this handler."""


class EventBus(ABC):
    """The Mediator: routes published events to every subscribed handler.

    Publishers and handlers never reference each other directly — all
    coordination happens here.
    """

    @abstractmethod
    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Register `handler` to receive events of `event_type`."""

    @abstractmethod
    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """Remove `handler` from the subscribers of `event_type`."""

    @abstractmethod
    def publish(self, event_type: str, payload: dict[str, object]) -> Event:
        """Publish a new event and dispatch it to every subscribed handler."""
