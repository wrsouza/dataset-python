"""Composition root: wires concrete adapters into a ready-to-use JobFacade."""

from __future__ import annotations

from jobs.application.facade import JobFacade
from jobs.infrastructure.celery_app import app as celery_app
from jobs.infrastructure.celery_task_queue import CeleryTaskQueue
from jobs.infrastructure.django_job_repository import DjangoJobRepository


def build_job_facade() -> JobFacade:
    """Construct a JobFacade backed by Celery/Redis and the Django ORM."""
    celery_adapter = CeleryTaskQueue(celery_app)
    return JobFacade(
        task_queue=celery_adapter,
        status_reader=celery_adapter,
        repository=DjangoJobRepository(),
    )
