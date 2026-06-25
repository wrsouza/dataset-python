"""Domain exceptions for the Remote File Proxy."""

from __future__ import annotations


class RemoteFileError(Exception):
    """Base class for every error raised by the remote_files domain."""


class FileNotFoundInRemoteError(RemoteFileError):
    """Raised when a requested object does not exist in the remote bucket."""

    def __init__(self, bucket: str, key: str) -> None:
        self.bucket = bucket
        self.key = key
        super().__init__(f"Object '{key}' not found in bucket '{bucket}'")


class RemoteStorageError(RemoteFileError):
    """Raised when the remote storage backend fails unexpectedly."""

    def __init__(self, bucket: str, key: str, reason: str) -> None:
        self.bucket = bucket
        self.key = key
        self.reason = reason
        super().__init__(
            f"Remote storage failure for '{key}' in bucket '{bucket}': {reason}"
        )


class CacheEvictionError(RemoteFileError):
    """Raised when an invalidate() call targets a key that was never cached."""

    def __init__(self, key: str) -> None:
        self.key = key
        super().__init__(f"Cannot evict '{key}': it was never cached")
