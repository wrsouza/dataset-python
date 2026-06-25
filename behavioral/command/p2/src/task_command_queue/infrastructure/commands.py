"""Concrete commands and the registry used to build them from a payload."""

from __future__ import annotations

from collections.abc import Callable

from task_command_queue.domain.interfaces import TaskCommand
from task_command_queue.infrastructure.receivers import EmailReceiver, ReportReceiver


class SendEmailCommand(TaskCommand):
    """Encapsulates sending a single email."""

    def __init__(
        self, receiver: EmailReceiver, to: str, subject: str, body: str
    ) -> None:
        self._receiver = receiver
        self._to = to
        self._subject = subject
        self._body = body

    def execute(self) -> str:
        return self._receiver.send(self._to, self._subject, self._body)

    def get_command_name(self) -> str:
        return "send_email"

    def to_payload(self) -> dict[str, object]:
        return {"to": self._to, "subject": self._subject, "body": self._body}


class GenerateReportCommand(TaskCommand):
    """Encapsulates generating a single report."""

    def __init__(
        self, receiver: ReportReceiver, report_type: str, parameters: dict[str, object]
    ) -> None:
        self._receiver = receiver
        self._report_type = report_type
        self._parameters = parameters

    def execute(self) -> str:
        return self._receiver.generate(self._report_type, self._parameters)

    def get_command_name(self) -> str:
        return "generate_report"

    def to_payload(self) -> dict[str, object]:
        return {"report_type": self._report_type, "parameters": self._parameters}


CommandFactory = Callable[[dict[str, object]], TaskCommand]


def _build_send_email(payload: dict[str, object]) -> TaskCommand:
    return SendEmailCommand(
        receiver=EmailReceiver(),
        to=str(payload["to"]),
        subject=str(payload["subject"]),
        body=str(payload["body"]),
    )


def _build_generate_report(payload: dict[str, object]) -> TaskCommand:
    parameters = payload.get("parameters", {})
    assert isinstance(parameters, dict)
    return GenerateReportCommand(
        receiver=ReportReceiver(),
        report_type=str(payload["report_type"]),
        parameters=parameters,
    )


COMMAND_REGISTRY: dict[str, CommandFactory] = {
    "send_email": _build_send_email,
    "generate_report": _build_generate_report,
}


class UnknownCommandError(ValueError):
    """Raised when a command name has no matching factory in the registry."""


def build_command(command_name: str, payload: dict[str, object]) -> TaskCommand:
    """Build a concrete TaskCommand from its name and payload via the registry."""
    factory = COMMAND_REGISTRY.get(command_name)
    if factory is None:
        available = ", ".join(sorted(COMMAND_REGISTRY))
        raise UnknownCommandError(
            f"Unknown command '{command_name}'. Available: {available}"
        )
    return factory(payload)
