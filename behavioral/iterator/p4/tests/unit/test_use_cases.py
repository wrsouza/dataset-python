"""Unit tests for WalkTreeUseCase and SummarizeTreeUseCase."""

from __future__ import annotations

from file_tree_iterator.application.use_cases import (
    SummarizeTreeUseCase,
    WalkTreeUseCase,
)
from tests.unit.test_dfs_iterator import FakeFileSystemSource, _dir, _file


def test_walk_tree_yields_every_entry_depth_first() -> None:
    source = FakeFileSystemSource(
        {
            "/root": [_dir("/root/sub"), _file("/root/z")],
            "/root/sub": [_file("/root/sub/x")],
        }
    )
    use_case = WalkTreeUseCase(source)

    paths = [entry.path for entry in use_case.execute("/root")]

    assert paths == ["/root/sub", "/root/sub/x", "/root/z"]


def test_summarize_tree_counts_files_directories_and_size() -> None:
    source = FakeFileSystemSource(
        {
            "/root": [_dir("/root/sub"), _file("/root/z", size=10)],
            "/root/sub": [_file("/root/sub/x", size=5)],
        }
    )
    use_case = SummarizeTreeUseCase(source)

    summary = use_case.execute("/root")

    assert summary.file_count == 2
    assert summary.directory_count == 1
    assert summary.total_size_bytes == 15


def test_summarize_empty_tree_returns_zeroes() -> None:
    source = FakeFileSystemSource({"/root": []})
    use_case = SummarizeTreeUseCase(source)

    summary = use_case.execute("/root")

    assert summary.file_count == 0
    assert summary.directory_count == 0
    assert summary.total_size_bytes == 0
