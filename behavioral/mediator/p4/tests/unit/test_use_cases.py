"""Unit tests for SendMessageUseCase and ReceiveMessagesUseCase."""

from __future__ import annotations

from service_bus.application.use_cases import (
    ReceiveMessagesUseCase,
    SendMessageUseCase,
)
from service_bus.domain.entities import ServiceMessage
from service_bus.domain.interfaces import ServiceBusMediator


class FakeServiceBusMediator(ServiceBusMediator):
    def __init__(self) -> None:
        self._queue: list[ServiceMessage] = []

    def send(self, sender_service: str, payload: dict[str, object]) -> ServiceMessage:
        message = ServiceMessage(sender_service=sender_service, payload=payload)
        self._queue.append(message)
        return message

    def receive(self, max_messages: int) -> list[ServiceMessage]:
        taken = self._queue[:max_messages]
        self._queue = self._queue[max_messages:]
        return taken


def test_send_use_case_delegates_to_mediator() -> None:
    mediator = FakeServiceBusMediator()
    use_case = SendMessageUseCase(mediator)

    message = use_case.execute("billing-service", {"invoice_id": "i-1"})

    assert message.sender_service == "billing-service"


def test_receive_use_case_returns_pending_messages() -> None:
    mediator = FakeServiceBusMediator()
    SendMessageUseCase(mediator).execute("billing-service", {"invoice_id": "i-1"})

    messages = ReceiveMessagesUseCase(mediator).execute(max_messages=10)

    assert len(messages) == 1
    assert messages[0].sender_service == "billing-service"
