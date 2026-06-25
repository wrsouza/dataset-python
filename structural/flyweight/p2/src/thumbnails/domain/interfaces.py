"""Domain interfaces (Protocols) for the thumbnail service — DIP boundary."""

from __future__ import annotations

from typing import Protocol

from thumbnails.domain.entities import ImageThumbnail, ThumbnailSpec


class ThumbnailSpecFactoryProtocol(Protocol):
    """Factory that manages the pool of shared ThumbnailSpec flyweights."""

    def get_or_create(
        self,
        width: int,
        height: int,
        quality: int,
        format: str,
        filters: tuple[str, ...],
    ) -> ThumbnailSpec: ...

    def get_all_specs(self) -> dict[str, ThumbnailSpec]: ...

    def spec_count(self) -> int: ...


class ImageStorageProtocol(Protocol):
    """Abstraction for binary image storage (S3, local disk, etc.)."""

    def upload(self, key: str, data: bytes, content_type: str) -> str: ...

    def download(self, key: str) -> bytes: ...

    def exists(self, key: str) -> bool: ...

    def get_url(self, key: str) -> str: ...


class ThumbnailRepositoryProtocol(Protocol):
    """Persistence for ImageThumbnail contexts."""

    def save(self, thumbnail: ImageThumbnail) -> None: ...

    def find(self, image_key: str, spec_key: str) -> ImageThumbnail | None: ...

    def count(self) -> int: ...
