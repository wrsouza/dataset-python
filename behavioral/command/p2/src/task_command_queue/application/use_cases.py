"""Use cases orchestrating command construction, execution, and publishing."""

from __future__ import annotations

from task_command_queue.domain.entities import TaskRecord
from task_command_queue.domain.interfaces import TaskPublisher
from task_command_queue.infrastructure.commands import build_command
from task_command_queue.infrastructure.invoker import TaskQueueInvoker


class TaskNotFoundError(Exception):
    """Raised when a task id has no matching record in the invoker history."""


class EnqueueTaskUseCase:
    """Builds a command from a registry entry, runs it, and publishes it."""

    def __init__(self, invoker: TaskQueueInvoker, publisher: TaskPublisher) -> None:
        self._invoker = invoker
        self._publisher = publisher

    def execute(self, command_name: str, payload: dict[str, object]) -> TaskRecord:
        command = build_command(command_name, payload)
        record = self._invoker.execute(command)
        self._publisher.publish(command.get_command_name(), command.to_payload())
        return record


class GetTaskUseCase:
    """Fetches a previously executed task's record by id."""

    def __init__(self, invoker: TaskQueueInvoker) -> None:
        self._invoker = invoker

    def execute(self, task_id: str) -> TaskRecord:
        record = self._invoker.get(task_id)
        if record is None:
            raise TaskNotFoundError(f"Task {task_id} not found")
        return record
