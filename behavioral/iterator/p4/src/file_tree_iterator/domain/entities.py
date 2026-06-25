"""Core entities for the file tree iteration domain."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FileEntry:
    """A single filesystem entry — the element type this Iterator traverses."""

    path: str
    size: int
    is_directory: bool


@dataclass(frozen=True)
class TreeSummary:
    """Aggregate statistics computed by iterating an entire directory tree."""

    file_count: int
    directory_count: int
    total_size_bytes: int
