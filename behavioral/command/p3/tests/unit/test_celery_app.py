"""Unit tests for the Celery task, run in eager mode (no real broker)."""

from __future__ import annotations

from scheduled_executor.infrastructure.celery_app import app, run_command_task


def test_task_is_eager_in_test_settings() -> None:
    assert app.conf.task_always_eager is True


def test_run_command_task_executes_cleanup() -> None:
    result = run_command_task.delay("cleanup", {"older_than_days": 14})

    assert "14" in result.get(timeout=5.0)


def test_run_command_task_executes_backup() -> None:
    result = run_command_task.delay("backup", {"target": "analytics-db"})

    assert "analytics-db" in result.get(timeout=5.0)
