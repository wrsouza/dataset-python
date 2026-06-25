"""Django ORM-backed implementation of ExecutionRepository."""

from __future__ import annotations

from scheduled_executor.django_app.models import ExecutionRecordModel
from scheduled_executor.domain.entities import ExecutionRecord, ExecutionStatus
from scheduled_executor.domain.interfaces import ExecutionRepository


class DjangoExecutionRepository(ExecutionRepository):
    """Persists execution records via the Django ORM."""

    def save(self, record: ExecutionRecord) -> None:
        ExecutionRecordModel.objects.update_or_create(
            job_id=record.job_id,
            defaults={
                "command_name": record.command_name,
                "status": record.status.value,
                "result_message": record.result_message,
                "executed_at": record.executed_at,
            },
        )

    def get(self, job_id: str) -> ExecutionRecord | None:
        model = ExecutionRecordModel.objects.filter(job_id=job_id).first()
        if model is None:
            return None
        return ExecutionRecord(
            job_id=model.job_id,
            command_name=model.command_name,
            status=ExecutionStatus(model.status),
            result_message=model.result_message,
            executed_at=model.executed_at,
        )
