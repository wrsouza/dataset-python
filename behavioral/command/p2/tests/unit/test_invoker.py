"""Unit tests for TaskQueueInvoker."""

from __future__ import annotations

from task_command_queue.domain.entities import TaskStatus
from task_command_queue.domain.interfaces import TaskCommand
from task_command_queue.infrastructure.invoker import TaskQueueInvoker


class _OkCommand(TaskCommand):
    def execute(self) -> str:
        return "done"

    def get_command_name(self) -> str:
        return "ok_command"

    def to_payload(self) -> dict[str, object]:
        return {}


class _FailingCommand(TaskCommand):
    def execute(self) -> str:
        raise RuntimeError("boom")

    def get_command_name(self) -> str:
        return "failing_command"

    def to_payload(self) -> dict[str, object]:
        return {}


def test_execute_records_completed_task() -> None:
    invoker = TaskQueueInvoker()

    record = invoker.execute(_OkCommand())

    assert record.status == TaskStatus.COMPLETED
    assert record.result_message == "done"
    assert invoker.get(record.task_id) is record


def test_execute_records_failed_task_when_command_raises() -> None:
    invoker = TaskQueueInvoker()

    record = invoker.execute(_FailingCommand())

    assert record.status == TaskStatus.FAILED
    assert "boom" in record.result_message


def test_get_returns_none_for_unknown_task_id() -> None:
    invoker = TaskQueueInvoker()

    assert invoker.get("missing") is None
