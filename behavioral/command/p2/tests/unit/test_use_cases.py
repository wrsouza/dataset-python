"""Unit tests for the enqueue/get task use cases."""

from __future__ import annotations

import pytest

from task_command_queue.application.use_cases import (
    EnqueueTaskUseCase,
    GetTaskUseCase,
    TaskNotFoundError,
)
from task_command_queue.domain.entities import TaskStatus
from task_command_queue.domain.interfaces import TaskPublisher
from task_command_queue.infrastructure.invoker import TaskQueueInvoker


class FakeTaskPublisher(TaskPublisher):
    def __init__(self) -> None:
        self.published: list[tuple[str, dict[str, object]]] = []

    def publish(self, command_name: str, payload: dict[str, object]) -> None:
        self.published.append((command_name, payload))


def test_enqueue_task_executes_and_publishes() -> None:
    invoker = TaskQueueInvoker()
    publisher = FakeTaskPublisher()
    use_case = EnqueueTaskUseCase(invoker, publisher)

    record = use_case.execute(
        "send_email", {"to": "a@b.com", "subject": "Hi", "body": "Hello"}
    )

    assert record.status == TaskStatus.COMPLETED
    assert publisher.published == [
        ("send_email", {"to": "a@b.com", "subject": "Hi", "body": "Hello"})
    ]


def test_get_task_returns_record_after_enqueue() -> None:
    invoker = TaskQueueInvoker()
    publisher = FakeTaskPublisher()
    enqueue_use_case = EnqueueTaskUseCase(invoker, publisher)
    get_use_case = GetTaskUseCase(invoker)

    record = enqueue_use_case.execute(
        "generate_report", {"report_type": "sales", "parameters": {}}
    )

    fetched = get_use_case.execute(record.task_id)

    assert fetched.task_id == record.task_id


def test_get_task_raises_when_not_found() -> None:
    get_use_case = GetTaskUseCase(TaskQueueInvoker())

    with pytest.raises(TaskNotFoundError):
        get_use_case.execute("missing")
