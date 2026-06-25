"""Unit tests for File (Leaf) and Directory (Composite) entities."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from filesystem.domain.entities import Directory, File
from filesystem.domain.interfaces import FSNode
from filesystem.infrastructure.s3_client import S3StorageClient

NOW = datetime(2026, 1, 1, tzinfo=UTC)


def make_file(
    key: str = "docs/readme.txt", storage: S3StorageClient | None = None
) -> File:
    return File(
        key=key,
        size=42,
        content_type="text/plain",
        last_modified=NOW,
        storage=storage,  # type: ignore[arg-type]
    )


class TestFile:
    def test_is_fsnode(self) -> None:
        assert isinstance(make_file(), FSNode)

    def test_get_size_returns_byte_count(self) -> None:
        assert make_file().get_size() == 42

    def test_get_path_returns_key(self) -> None:
        assert make_file("a/b.txt").get_path() == "a/b.txt"

    def test_list_contents_returns_single_entry(self) -> None:
        contents = make_file().list_contents()
        assert len(contents) == 1
        assert contents[0]["path"] == "docs/readme.txt"

    def test_to_dict_has_file_type_and_name(self) -> None:
        data = make_file("docs/readme.txt").to_dict()
        assert data["type"] == "file"
        assert data["name"] == "readme.txt"
        assert data["size"] == 42
        assert data["content_type"] == "text/plain"
        assert data["last_modified"] == NOW.isoformat()

    def test_delete_delegates_to_storage(self, storage: S3StorageClient) -> None:
        storage.put_file("docs/readme.txt", b"hello", "text/plain")
        file_node = make_file(storage=storage)

        file_node.delete()

        with pytest.raises(Exception):  # noqa: B017, PT011
            storage.get_node("docs/readme.txt")


class TestDirectory:
    def test_is_fsnode(self, storage: S3StorageClient) -> None:
        assert isinstance(Directory(path="a/", storage=storage), FSNode)

    def test_get_path_normalizes_trailing_slash(self, storage: S3StorageClient) -> None:
        directory = Directory(path="a/b", storage=storage)
        assert directory.get_path() == "a/b/"

    def test_lazy_loads_children_from_storage(self, storage: S3StorageClient) -> None:
        storage.put_folder("docs")
        storage.put_file("docs/a.txt", b"1", "text/plain")
        storage.put_file("docs/b.txt", b"22", "text/plain")

        directory = Directory(path="docs/", storage=storage)
        children = directory.get_children()

        assert {c.get_path() for c in children} == {"docs/a.txt", "docs/b.txt"}

    def test_children_loaded_only_once(self, storage: S3StorageClient) -> None:
        directory = Directory(path="docs/", storage=storage, children=[])
        directory.get_children()
        directory.get_children()
        assert directory._children == []  # noqa: SLF001

    def test_add_child_appends_node(self, storage: S3StorageClient) -> None:
        directory = Directory(path="docs/", storage=storage, children=[])
        file_node = make_file(storage=storage)

        directory.add_child(file_node)

        assert directory.get_children() == [file_node]

    def test_remove_child_removes_node(self, storage: S3StorageClient) -> None:
        file_node = make_file(storage=storage)
        directory = Directory(path="docs/", storage=storage, children=[file_node])

        directory.remove_child(file_node)

        assert directory.get_children() == []

    def test_get_size_sums_children_sizes(self, storage: S3StorageClient) -> None:
        children = [
            make_file("docs/a.txt", storage=storage),
            make_file("docs/b.txt", storage=storage),
        ]
        directory = Directory(path="docs/", storage=storage, children=children)

        assert directory.get_size() == 84

    def test_get_size_empty_directory_is_zero(self, storage: S3StorageClient) -> None:
        directory = Directory(path="empty/", storage=storage, children=[])
        assert directory.get_size() == 0

    def test_list_contents_flattens_nested_tree(self, storage: S3StorageClient) -> None:
        leaf_a = make_file("docs/a.txt", storage=storage)
        leaf_b = make_file("docs/sub/b.txt", storage=storage)
        sub_dir = Directory(path="docs/sub/", storage=storage, children=[leaf_b])
        root = Directory(path="docs/", storage=storage, children=[leaf_a, sub_dir])

        contents = root.list_contents()

        assert {c["path"] for c in contents} == {"docs/a.txt", "docs/sub/b.txt"}

    def test_to_dict_includes_nested_children(self, storage: S3StorageClient) -> None:
        leaf = make_file("docs/a.txt", storage=storage)
        directory = Directory(path="docs/", storage=storage, children=[leaf])

        data = directory.to_dict()

        assert data["type"] == "folder"
        assert data["name"] == "docs"
        assert data["size"] == 42
        assert data["children"][0]["path"] == "docs/a.txt"

    def test_delete_removes_children_then_self(self, storage: S3StorageClient) -> None:
        storage.put_folder("docs")
        storage.put_file("docs/a.txt", b"1", "text/plain")
        directory = Directory(path="docs/", storage=storage)
        directory.get_children()  # force load

        directory.delete()

        with pytest.raises(Exception):  # noqa: B017, PT011
            storage.get_node("docs")
