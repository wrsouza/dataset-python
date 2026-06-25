"""Unit tests for the trigger/get execution use cases."""

from __future__ import annotations

import pytest

from scheduled_executor.application.use_cases import (
    ExecutionNotFoundError,
    GetExecutionUseCase,
    TriggerCommandUseCase,
)
from scheduled_executor.domain.entities import ExecutionRecord, ExecutionStatus
from scheduled_executor.domain.interfaces import ExecutionRepository
from scheduled_executor.infrastructure.commands import UnknownCommandError


class FakeAsyncResult:
    def __init__(
        self, value: str | None = None, error: Exception | None = None
    ) -> None:
        self._value = value
        self._error = error

    def get(self, timeout: float) -> str:
        if self._error is not None:
            raise self._error
        assert self._value is not None
        return self._value


class FakeTask:
    def __init__(
        self, value: str | None = None, error: Exception | None = None
    ) -> None:
        self._value = value
        self._error = error
        self.calls: list[tuple[str, dict[str, object]]] = []

    def delay(self, command_name: str, payload: dict[str, object]) -> FakeAsyncResult:
        self.calls.append((command_name, payload))
        return FakeAsyncResult(self._value, self._error)


class InMemoryExecutionRepository(ExecutionRepository):
    def __init__(self) -> None:
        self._records: dict[str, ExecutionRecord] = {}

    def save(self, record: ExecutionRecord) -> None:
        self._records[record.job_id] = record

    def get(self, job_id: str) -> ExecutionRecord | None:
        return self._records.get(job_id)


def test_trigger_command_persists_success_record() -> None:
    task = FakeTask(value="Backup of 'orders-db' completed")
    repository = InMemoryExecutionRepository()
    use_case = TriggerCommandUseCase(task, repository)

    record = use_case.execute("backup", {"target": "orders-db"})

    assert record.status == ExecutionStatus.SUCCESS
    assert task.calls == [("backup", {"target": "orders-db"})]
    assert repository.get(record.job_id) is not None


def test_trigger_command_persists_failure_record_on_worker_error() -> None:
    task = FakeTask(error=RuntimeError("worker exploded"))
    repository = InMemoryExecutionRepository()
    use_case = TriggerCommandUseCase(task, repository)

    record = use_case.execute("backup", {"target": "orders-db"})

    assert record.status == ExecutionStatus.FAILURE
    assert "worker exploded" in record.result_message


def test_trigger_command_raises_for_unknown_command_without_dispatching() -> None:
    task = FakeTask(value="unused")
    use_case = TriggerCommandUseCase(task, InMemoryExecutionRepository())

    with pytest.raises(UnknownCommandError):
        use_case.execute("nope", {})

    assert task.calls == []


def test_get_execution_returns_persisted_record() -> None:
    repository = InMemoryExecutionRepository()
    trigger_use_case = TriggerCommandUseCase(FakeTask(value="done"), repository)
    get_use_case = GetExecutionUseCase(repository)

    record = trigger_use_case.execute("cleanup", {"older_than_days": 7})
    fetched = get_use_case.execute(record.job_id)

    assert fetched.job_id == record.job_id


def test_get_execution_raises_when_not_found() -> None:
    get_use_case = GetExecutionUseCase(InMemoryExecutionRepository())

    with pytest.raises(ExecutionNotFoundError):
        get_use_case.execute("missing")
