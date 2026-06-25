"""Concrete Iterator: depth-first walk of a directory tree, one entry at a time."""

from __future__ import annotations

from file_tree_iterator.domain.entities import FileEntry
from file_tree_iterator.domain.interfaces import FileSystemSource, FileTreeIterator


class DepthFirstFileIterator(FileTreeIterator):
    """Traverses every entry under a root directory, depth-first.

    Uses an explicit stack instead of recursion, and only ever loads one
    directory's direct children at a time via `FileSystemSource` — the
    client only ever sees `has_next`/`next`, never the stack underneath.
    """

    def __init__(self, source: FileSystemSource, root_path: str) -> None:
        self._source = source
        self._stack: list[FileEntry] = list(reversed(source.list_children(root_path)))

    def has_next(self) -> bool:
        return bool(self._stack)

    def next(self) -> FileEntry:
        if not self.has_next():
            raise StopIteration("No more entries to iterate")
        entry = self._stack.pop()
        if entry.is_directory:
            self._stack.extend(reversed(self._source.list_children(entry.path)))
        return entry
