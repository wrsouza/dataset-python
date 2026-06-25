"""Use cases orchestrating the FSNode tree (Composite pattern).

SRP: each use case has a single responsibility (lookup, compute, upload,
delete). DIP: every use case depends on `S3StorageClient`, injected via
the constructor, never instantiated internally.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from filesystem.infrastructure.s3_client import S3StorageClient


class GetTreeUseCase:
    """Resolve a path into its FSNode tree representation."""

    def __init__(self, storage: S3StorageClient) -> None:
        self._storage = storage

    def execute(self, path: str) -> dict[str, object]:
        """Return the serialised tree (file or folder) rooted at `path`."""
        node = self._storage.get_node(path)
        return node.to_dict()


class CalculateTotalSizeUseCase:
    """Calculate the total size in bytes of a node and its descendants.

    Demonstrates the key benefit of Composite: the client code does not
    care whether `path` points to a File or a Directory — `get_size()`
    is called uniformly through the FSNode interface.
    """

    def __init__(self, storage: S3StorageClient) -> None:
        self._storage = storage

    def execute(self, path: str) -> int:
        node = self._storage.get_node(path)
        return node.get_size()


class ListContentsUseCase:
    """List the flattened contents (all files) under a given path."""

    def __init__(self, storage: S3StorageClient) -> None:
        self._storage = storage

    def execute(self, path: str) -> list[dict[str, object]]:
        node = self._storage.get_node(path)
        return node.list_contents()


class UploadFileUseCase:
    """Upload raw bytes as a new file under the given S3 key."""

    def __init__(self, storage: S3StorageClient) -> None:
        self._storage = storage

    def execute(self, key: str, content: bytes, content_type: str) -> None:
        self._storage.put_file(key, content, content_type)


class CreateDirectoryUseCase:
    """Create an empty folder marker at the given path."""

    def __init__(self, storage: S3StorageClient) -> None:
        self._storage = storage

    def execute(self, path: str) -> None:
        self._storage.put_folder(path)


class DeleteNodeUseCase:
    """Delete a node (file or folder) and, for folders, all descendants.

    Polymorphism over the FSNode interface means a single call to
    `delete()` works identically for a File leaf or a Directory composite.
    """

    def __init__(self, storage: S3StorageClient) -> None:
        self._storage = storage

    def execute(self, path: str) -> None:
        node = self._storage.get_node(path)
        node.delete()
