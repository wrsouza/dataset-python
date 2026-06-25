"""Abstractions for the Iterator pattern and the underlying filesystem access."""

from __future__ import annotations

from abc import ABC, abstractmethod

from file_tree_iterator.domain.entities import FileEntry


class FileTreeIterator(ABC):
    """The Iterator: traverses every entry in a directory tree one at a time,

    without exposing how (depth-first, breadth-first, lazily or not) the
    traversal actually happens underneath.
    """

    @abstractmethod
    def has_next(self) -> bool:
        """Return True if there is at least one more entry to traverse."""

    @abstractmethod
    def next(self) -> FileEntry:
        """Return the next entry and advance the iterator's position."""


class FileSystemSource(ABC):
    """The Aggregate's data-access boundary: lists one directory's direct children."""

    @abstractmethod
    def list_children(self, directory_path: str) -> list[FileEntry]:
        """Return the immediate children of `directory_path`, files and subdirs."""
