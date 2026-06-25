"""Component ABC for the Composite pattern — FSNode hierarchy."""

from __future__ import annotations

from abc import ABC, abstractmethod


class FSNode(ABC):
    """Abstract Component: uniform interface for Files and Folders.

    Both S3File (leaf) and S3Folder (composite) implement this interface.
    Clients use only FSNode — no isinstance() checks required (LSP).
    """

    @abstractmethod
    def get_size(self) -> int:
        """Return the total size in bytes of this node and all descendants."""
        ...

    @abstractmethod
    def get_path(self) -> str:
        """Return the full S3 path/key for this node."""
        ...

    @abstractmethod
    def list_contents(self) -> list[dict[str, object]]:
        """Return a flat list of dicts describing all contained nodes."""
        ...

    @abstractmethod
    def delete(self) -> None:
        """Delete this node (and all descendants for folders) from S3."""
        ...

    @abstractmethod
    def to_dict(self) -> dict[str, object]:
        """Serialize this node to a JSON-serialisable dict."""
        ...
