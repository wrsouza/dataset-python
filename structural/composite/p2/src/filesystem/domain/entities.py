"""Leaf (File) and Composite (Directory) implementations of FSNode.

These classes are the heart of the Composite pattern: both represent a
node in the virtual file system tree and both honour the same FSNode
contract, so client code never needs `isinstance()` checks (LSP).
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from filesystem.domain.interfaces import FSNode

if TYPE_CHECKING:
    from filesystem.infrastructure.s3_client import S3StorageClient


class File(FSNode):
    """Leaf node: a single file backed by one S3 object.

    Satisfies LSP — every method returns valid data for a single-file
    node, so callers need no isinstance() checks.
    """

    def __init__(
        self,
        key: str,
        size: int,
        content_type: str,
        last_modified: datetime,
        storage: S3StorageClient,
    ) -> None:
        self._key = key
        self._size = size
        self._content_type = content_type
        self._last_modified = last_modified
        self._storage = storage

    def get_size(self) -> int:
        return self._size

    def get_path(self) -> str:
        return self._key

    def list_contents(self) -> list[dict[str, object]]:
        return [self.to_dict()]

    def delete(self) -> None:
        self._storage.delete_object(self._key)

    def to_dict(self) -> dict[str, object]:
        return {
            "type": "file",
            "path": self._key,
            "name": self._key.split("/")[-1],
            "size": self._size,
            "content_type": self._content_type,
            "last_modified": self._last_modified.isoformat(),
        }


class Directory(FSNode):
    """Composite node: a virtual folder containing child FSNodes.

    Children are lazy-loaded from S3 on first access (on-demand loading).
    OCP: new node types extend FSNode without modifying Directory.
    """

    def __init__(
        self,
        path: str,
        storage: S3StorageClient,
        children: list[FSNode] | None = None,
    ) -> None:
        self._path = path.rstrip("/") + "/"
        self._storage = storage
        self._children: list[FSNode] | None = children

    def _ensure_loaded(self) -> None:
        """Lazy-load children from S3 if not already loaded."""
        if self._children is None:
            self._children = self._storage.list_direct_children(self._path)

    def add_child(self, child: FSNode) -> None:
        self._ensure_loaded()
        assert self._children is not None  # noqa: S101
        self._children.append(child)

    def remove_child(self, child: FSNode) -> None:
        self._ensure_loaded()
        assert self._children is not None  # noqa: S101
        self._children.remove(child)

    def get_children(self) -> list[FSNode]:
        self._ensure_loaded()
        return list(self._children or [])

    def get_size(self) -> int:
        self._ensure_loaded()
        return sum(child.get_size() for child in (self._children or []))

    def get_path(self) -> str:
        return self._path

    def list_contents(self) -> list[dict[str, object]]:
        self._ensure_loaded()
        contents: list[dict[str, object]] = []
        for child in self._children or []:
            contents.extend(child.list_contents())
        return contents

    def delete(self) -> None:
        """Recursively delete all children then the folder marker."""
        self._ensure_loaded()
        for child in list(self._children or []):
            child.delete()
        self._storage.delete_object(self._path)

    def to_dict(self) -> dict[str, object]:
        self._ensure_loaded()
        return {
            "type": "folder",
            "path": self._path,
            "name": self._path.rstrip("/").split("/")[-1],
            "size": self.get_size(),
            "children": [child.to_dict() for child in (self._children or [])],
        }
