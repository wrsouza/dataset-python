"""Integration tests for the Typer CLI, with build_mediator monkeypatched."""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

import service_bus.main as main_module
from service_bus.domain.entities import ServiceMessage
from service_bus.domain.interfaces import ServiceBusMediator

runner = CliRunner()


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


@pytest.fixture
def fake_mediator(monkeypatch: pytest.MonkeyPatch) -> FakeServiceBusMediator:
    mediator = FakeServiceBusMediator()
    monkeypatch.setattr(main_module, "build_mediator", lambda: mediator)
    return mediator


def test_send_command_reports_success(fake_mediator: FakeServiceBusMediator) -> None:
    result = runner.invoke(
        main_module.app, ["send", "billing-service", '{"invoice_id": "i-1"}']
    )

    assert result.exit_code == 0
    assert "billing-service" in result.stdout


def test_receive_command_lists_pending_messages(
    fake_mediator: FakeServiceBusMediator,
) -> None:
    fake_mediator.send("billing-service", {"invoice_id": "i-1"})

    result = runner.invoke(main_module.app, ["receive"])

    assert result.exit_code == 0
    assert "billing-service" in result.stdout


def test_receive_command_reports_when_empty(
    fake_mediator: FakeServiceBusMediator,
) -> None:
    result = runner.invoke(main_module.app, ["receive"])

    assert result.exit_code == 0
    assert "No messages available" in result.stdout
