"""Integration tests for OsFileSystemSource against a real temp directory."""

from __future__ import annotations

from pathlib import Path

from file_tree_iterator.infrastructure.filesystem_source import OsFileSystemSource


def test_list_children_returns_files_and_directories(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("hello")
    (tmp_path / "subdir").mkdir()

    source = OsFileSystemSource()
    children = source.list_children(str(tmp_path))

    names = {Path(c.path).name for c in children}
    assert names == {"a.txt", "subdir"}


def test_list_children_reports_file_size(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("hello")

    source = OsFileSystemSource()
    [entry] = source.list_children(str(tmp_path))

    assert entry.is_directory is False
    assert entry.size == 5


def test_list_children_directory_has_zero_size(tmp_path: Path) -> None:
    (tmp_path / "subdir").mkdir()

    source = OsFileSystemSource()
    [entry] = source.list_children(str(tmp_path))

    assert entry.is_directory is True
    assert entry.size == 0


def test_list_children_returns_empty_for_empty_directory(tmp_path: Path) -> None:
    source = OsFileSystemSource()

    assert source.list_children(str(tmp_path)) == []
