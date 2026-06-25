"""Subject interface of the Proxy pattern.

FileResource is the abstraction shared by the RealSubject (RealS3File, a
direct boto3-backed download) and the Proxy (RemoteFileProxy, which adds
lazy loading and caching). Application and CLI code depend only on this
Protocol, never on a concrete implementation (DIP).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class FileResource(Protocol):
    """Something that behaves like a remote file: readable, sized, checkable."""

    def read(self) -> bytes:
        """Return the full file content, downloading it if not yet cached."""

    def exists(self) -> bool:
        """Return whether the file exists in the remote storage."""

    @property
    def size(self) -> int:
        """Return the file size in bytes, without necessarily downloading it."""

    @property
    def key(self) -> str:
        """Return the object key (path) identifying this file."""
