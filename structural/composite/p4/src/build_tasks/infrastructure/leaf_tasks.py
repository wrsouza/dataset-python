"""Leaf implementations of `BuildTask`.

Each leaf wraps one concrete way of "doing work": running a shell command,
calling a Python callable, or simulating work for didactic/demo purposes.
Adding a new leaf type (e.g. an HTTP health-check task) means writing a new
class here — `TaskGroup` and the rest of the system never need to change.
This is the Open/Closed Principle in action.
"""

from __future__ import annotations

import subprocess
import time
from collections.abc import Callable

from src.build_tasks.domain.entities import TaskResult, TaskStatus
from src.build_tasks.domain.exceptions import TaskExecutionError
from src.build_tasks.domain.interfaces import BuildTask

SHELL_COMMAND_TIMEOUT_SECONDS = 60


class ShellCommandTask(BuildTask):
    """Leaf that executes a shell command via `subprocess`."""

    def __init__(self, name: str, command: str) -> None:
        self._name = name
        self._command = command

    @property
    def name(self) -> str:
        return self._name

    def estimated_duration_seconds(self) -> float:
        return 1.0

    def execute(self) -> TaskResult:
        started_at = time.monotonic()
        try:
            completed = subprocess.run(  # noqa: S602, S603
                self._command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=SHELL_COMMAND_TIMEOUT_SECONDS,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise TaskExecutionError(self._name, "command timed out") from exc

        duration = time.monotonic() - started_at
        if completed.returncode != 0:
            return TaskResult(
                task_name=self._name,
                status=TaskStatus.FAILURE,
                duration_seconds=duration,
                message=completed.stderr.strip() or "non-zero exit code",
            )
        return TaskResult(
            task_name=self._name,
            status=TaskStatus.SUCCESS,
            duration_seconds=duration,
            message=completed.stdout.strip(),
        )


class PythonFunctionTask(BuildTask):
    """Leaf that executes an in-process Python callable."""

    def __init__(self, name: str, func: Callable[[], None]) -> None:
        self._name = name
        self._func = func

    @property
    def name(self) -> str:
        return self._name

    def estimated_duration_seconds(self) -> float:
        return 0.5

    def execute(self) -> TaskResult:
        started_at = time.monotonic()
        try:
            self._func()
        except Exception as exc:  # noqa: BLE001
            duration = time.monotonic() - started_at
            return TaskResult(
                task_name=self._name,
                status=TaskStatus.FAILURE,
                duration_seconds=duration,
                message=str(exc),
            )
        duration = time.monotonic() - started_at
        return TaskResult(
            task_name=self._name,
            status=TaskStatus.SUCCESS,
            duration_seconds=duration,
        )


class SimulatedTask(BuildTask):
    """Leaf that fakes work for demos and tests, without real side effects.

    Useful in a learning dataset: it lets the tree shape and the Composite
    pattern be exercised deterministically, without needing a real shell or
    a real Python build step.
    """

    def __init__(
        self,
        name: str,
        duration_seconds: float = 0.1,
        should_succeed: bool = True,
    ) -> None:
        self._name = name
        self._duration_seconds = duration_seconds
        self._should_succeed = should_succeed

    @property
    def name(self) -> str:
        return self._name

    def estimated_duration_seconds(self) -> float:
        return self._duration_seconds

    def execute(self) -> TaskResult:
        if self._should_succeed:
            return TaskResult(
                task_name=self._name,
                status=TaskStatus.SUCCESS,
                duration_seconds=self._duration_seconds,
                message="simulated success",
            )
        return TaskResult(
            task_name=self._name,
            status=TaskStatus.FAILURE,
            duration_seconds=self._duration_seconds,
            message="simulated failure",
        )
