"""The Invoker: runs commands and keeps a history of their outcomes."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from task_command_queue.domain.entities import TaskRecord, TaskStatus
from task_command_queue.domain.interfaces import TaskCommand


class TaskQueueInvoker:
    """Executes TaskCommands and records the result of each in history.

    The invoker never knows what a command does internally — it only
    knows the TaskCommand contract (execute / get_command_name).
    """

    def __init__(self) -> None:
        self._history: dict[str, TaskRecord] = {}

    def execute(self, command: TaskCommand) -> TaskRecord:
        task_id = str(uuid.uuid4())
        try:
            result_message = command.execute()
            record = TaskRecord(
                task_id=task_id,
                command_name=command.get_command_name(),
                status=TaskStatus.COMPLETED,
                result_message=result_message,
                executed_at=datetime.now(UTC),
            )
        except Exception as exc:  # any receiver failure becomes a FAILED record
            record = TaskRecord(
                task_id=task_id,
                command_name=command.get_command_name(),
                status=TaskStatus.FAILED,
                result_message=str(exc),
                executed_at=datetime.now(UTC),
            )
        self._history[task_id] = record
        return record

    def get(self, task_id: str) -> TaskRecord | None:
        return self._history.get(task_id)
