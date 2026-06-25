"""SQLite-backed repository for DownloadJob — persists the FSM's
current state name across CLI invocations (each command is a separate
process).

OCP: a new state only needs an entry in `_STATE_REGISTRY` for the
repository to be able to rehydrate it; no other infrastructure code
changes.
"""

from __future__ import annotations

import sqlite3

from download_manager_fsm.domain.entities import DownloadJob
from download_manager_fsm.domain.interfaces import DownloadState
from download_manager_fsm.infrastructure.states.completed import CompletedState
from download_manager_fsm.infrastructure.states.downloading import DownloadingState
from download_manager_fsm.infrastructure.states.failed import FailedState
from download_manager_fsm.infrastructure.states.idle import IdleState
from download_manager_fsm.infrastructure.states.paused import PausedState

_STATE_REGISTRY: dict[str, type[DownloadState]] = {
    "Idle": IdleState,
    "Downloading": DownloadingState,
    "Paused": PausedState,
    "Completed": CompletedState,
    "Failed": FailedState,
}

_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS download_job (
    job_id TEXT PRIMARY KEY,
    s3_key TEXT NOT NULL,
    state TEXT NOT NULL,
    bytes_downloaded INTEGER NOT NULL DEFAULT 0,
    failure_reason TEXT NOT NULL DEFAULT ''
)
"""


class SqliteDownloadJobRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self._connection.execute(_TABLE_SQL)
        self._connection.commit()

    def save(self, job: DownloadJob) -> None:
        self._connection.execute(
            "INSERT INTO download_job (job_id, s3_key, state, bytes_downloaded, "
            "failure_reason) VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(job_id) DO UPDATE SET "
            "s3_key = excluded.s3_key, state = excluded.state, "
            "bytes_downloaded = excluded.bytes_downloaded, "
            "failure_reason = excluded.failure_reason",
            (
                job.job_id,
                job.s3_key,
                job.get_current_state_name(),
                job.bytes_downloaded,
                job.failure_reason,
            ),
        )
        self._connection.commit()

    def find_by_id(self, job_id: str) -> DownloadJob | None:
        row = self._connection.execute(
            "SELECT s3_key, state, bytes_downloaded, failure_reason "
            "FROM download_job WHERE job_id = ?",
            (job_id,),
        ).fetchone()
        if row is None:
            return None

        job = DownloadJob(job_id=job_id, s3_key=row[0])
        job.bytes_downloaded = row[2]
        job.failure_reason = row[3]
        job._state = _STATE_REGISTRY[row[1]]()  # noqa: SLF001
        return job
