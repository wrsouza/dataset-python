"""Abstractions for the Mediator pattern over an AWS SQS-backed service bus."""

from __future__ import annotations

from abc import ABC, abstractmethod

from service_bus.domain.entities import ServiceMessage


class ServiceBusMediator(ABC):
    """The Mediator: routes messages between services via a shared queue.

    Services never address one another directly — a sender only knows
    the bus, and a receiver only knows the bus, never who's on the other
    end.
    """

    @abstractmethod
    def send(self, sender_service: str, payload: dict[str, object]) -> ServiceMessage:
        """Place a message from `sender_service` onto the bus."""

    @abstractmethod
    def receive(self, max_messages: int) -> list[ServiceMessage]:
        """Pull up to `max_messages` pending messages off the bus, removing them."""
