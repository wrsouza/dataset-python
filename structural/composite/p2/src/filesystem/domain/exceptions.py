"""Domain exceptions for the Virtual File System."""

from __future__ import annotations


class FSNodeNotFoundError(Exception):
    """Raised when a path does not exist in S3."""

    def __init__(self, path: str) -> None:
        super().__init__(f"Path not found: {path!r}")
        self.path = path


class FSNodeAlreadyExistsError(Exception):
    """Raised when trying to create a node that already exists."""

    def __init__(self, path: str) -> None:
        super().__init__(f"Path already exists: {path!r}")
        self.path = path


class FSStorageError(Exception):
    """Raised when the underlying storage (S3) returns an unexpected error."""
