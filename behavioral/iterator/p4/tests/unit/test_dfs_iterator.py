"""Unit tests for DepthFirstFileIterator using a fake in-memory filesystem."""

from __future__ import annotations

import pytest

from file_tree_iterator.domain.entities import FileEntry
from file_tree_iterator.domain.interfaces import FileSystemSource
from file_tree_iterator.infrastructure.dfs_iterator import DepthFirstFileIterator


class FakeFileSystemSource(FileSystemSource):
    """An in-memory filesystem: maps directory path -> its direct children."""

    def __init__(self, tree: dict[str, list[FileEntry]]) -> None:
        self._tree = tree
        self.list_calls = 0

    def list_children(self, directory_path: str) -> list[FileEntry]:
        self.list_calls += 1
        return self._tree.get(directory_path, [])


def _file(path: str, size: int = 1) -> FileEntry:
    return FileEntry(path=path, size=size, is_directory=False)


def _dir(path: str) -> FileEntry:
    return FileEntry(path=path, size=0, is_directory=True)


def test_iterates_flat_directory() -> None:
    source = FakeFileSystemSource({"/root": [_file("/root/a"), _file("/root/b")]})
    iterator = DepthFirstFileIterator(source, "/root")

    seen = []
    while iterator.has_next():
        seen.append(iterator.next().path)

    assert seen == ["/root/a", "/root/b"]


def test_descends_into_subdirectories_depth_first() -> None:
    source = FakeFileSystemSource(
        {
            "/root": [_dir("/root/sub"), _file("/root/z")],
            "/root/sub": [_file("/root/sub/x")],
        }
    )
    iterator = DepthFirstFileIterator(source, "/root")

    seen = []
    while iterator.has_next():
        seen.append(iterator.next().path)

    assert seen == ["/root/sub", "/root/sub/x", "/root/z"]


def test_has_next_is_false_for_empty_directory() -> None:
    source = FakeFileSystemSource({"/root": []})
    iterator = DepthFirstFileIterator(source, "/root")

    assert iterator.has_next() is False


def test_next_raises_stop_iteration_when_exhausted() -> None:
    source = FakeFileSystemSource({"/root": [_file("/root/a")]})
    iterator = DepthFirstFileIterator(source, "/root")
    iterator.next()

    with pytest.raises(StopIteration):
        iterator.next()


def test_only_lists_a_directory_when_descended_into() -> None:
    source = FakeFileSystemSource(
        {"/root": [_file("/root/a")], "/root/unused": [_file("/root/unused/x")]}
    )
    iterator = DepthFirstFileIterator(source, "/root")
    iterator.next()

    assert source.list_calls == 1
