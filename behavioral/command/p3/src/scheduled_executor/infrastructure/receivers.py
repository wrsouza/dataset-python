"""Receivers: the objects that know how to perform the actual scheduled work."""

from __future__ import annotations


class CleanupReceiver:
    """Knows how to purge stale records. Stands in for a real cleanup job."""

    def purge(self, older_than_days: int) -> str:
        return f"Purged records older than {older_than_days} day(s)"


class BackupReceiver:
    """Knows how to back up a dataset. Stands in for a real backup job."""

    def backup(self, target: str) -> str:
        return f"Backup of '{target}' completed"
