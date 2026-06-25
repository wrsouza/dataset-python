"""Use cases orchestrating sending and receiving messages through the bus."""

from __future__ import annotations

from service_bus.domain.entities import ServiceMessage
from service_bus.domain.interfaces import ServiceBusMediator


class SendMessageUseCase:
    """Sends a message from one service onto the bus."""

    def __init__(self, mediator: ServiceBusMediator) -> None:
        self._mediator = mediator

    def execute(
        self, sender_service: str, payload: dict[str, object]
    ) -> ServiceMessage:
        return self._mediator.send(sender_service, payload)


class ReceiveMessagesUseCase:
    """Pulls pending messages off the bus for a consuming service."""

    def __init__(self, mediator: ServiceBusMediator) -> None:
        self._mediator = mediator

    def execute(self, max_messages: int) -> list[ServiceMessage]:
        return self._mediator.receive(max_messages)
