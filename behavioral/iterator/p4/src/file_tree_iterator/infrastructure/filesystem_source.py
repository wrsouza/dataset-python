"""os.scandir-backed implementation of FileSystemSource."""

from __future__ import annotations

import os

from file_tree_iterator.domain.entities import FileEntry
from file_tree_iterator.domain.interfaces import FileSystemSource


class OsFileSystemSource(FileSystemSource):
    """Lists a single directory's direct children via `os.scandir`."""

    def list_children(self, directory_path: str) -> list[FileEntry]:
        entries = []
        with os.scandir(directory_path) as scanner:
            for entry in scanner:
                is_directory = entry.is_dir(follow_symlinks=False)
                size = 0 if is_directory else entry.stat().st_size
                entries.append(
                    FileEntry(path=entry.path, size=size, is_directory=is_directory)
                )
        return entries
