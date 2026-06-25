"""Builds the final MigrationReport from per-table results."""

from __future__ import annotations

from datetime import datetime

from migration.domain.entities import MigrationReport, TableMigrationResult


class SimpleMigrationReporter:
    def build_report(
        self,
        migration_id: str,
        table_results: list[TableMigrationResult],
        started_at: datetime,
        finished_at: datetime,
    ) -> MigrationReport:
        return MigrationReport(
            migration_id=migration_id,
            tables=table_results,
            started_at=started_at,
            finished_at=finished_at,
        )
