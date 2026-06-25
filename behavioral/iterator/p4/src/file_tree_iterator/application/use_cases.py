"""Use cases orchestrating tree traversal and full-tree aggregation."""

from __future__ import annotations

from collections.abc import Iterator as TypingIterator

from file_tree_iterator.domain.entities import FileEntry, TreeSummary
from file_tree_iterator.domain.interfaces import FileSystemSource
from file_tree_iterator.infrastructure.dfs_iterator import DepthFirstFileIterator


class WalkTreeUseCase:
    """Yields every entry under a root directory, depth-first, via the Iterator."""

    def __init__(self, source: FileSystemSource) -> None:
        self._source = source

    def execute(self, root_path: str) -> TypingIterator[FileEntry]:
        iterator = DepthFirstFileIterator(self._source, root_path)
        while iterator.has_next():
            yield iterator.next()


class SummarizeTreeUseCase:
    """Aggregates file/directory counts and total size by iterating the tree."""

    def __init__(self, source: FileSystemSource) -> None:
        self._source = source

    def execute(self, root_path: str) -> TreeSummary:
        iterator = DepthFirstFileIterator(self._source, root_path)
        file_count = 0
        directory_count = 0
        total_size = 0

        while iterator.has_next():
            entry = iterator.next()
            if entry.is_directory:
                directory_count += 1
            else:
                file_count += 1
                total_size += entry.size

        return TreeSummary(
            file_count=file_count,
            directory_count=directory_count,
            total_size_bytes=total_size,
        )
