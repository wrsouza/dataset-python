"""In-memory repository for ImageThumbnail contexts."""

from __future__ import annotations

from thumbnails.domain.entities import ImageThumbnail


class InMemoryThumbnailRepository:
    """Stores ImageThumbnail contexts in a dict keyed by (image_key, spec_key).

    In production this could be replaced with a database-backed implementation
    without changing application-layer code (DIP compliance).
    """

    def __init__(self) -> None:
        self._store: dict[tuple[str, str], ImageThumbnail] = {}

    def save(self, thumbnail: ImageThumbnail) -> None:
        """Persist a thumbnail context."""
        key = (thumbnail.image_key, thumbnail.spec.spec_key)
        self._store[key] = thumbnail

    def find(self, image_key: str, spec_key: str) -> ImageThumbnail | None:
        """Return existing thumbnail or None."""
        return self._store.get((image_key, spec_key))

    def count(self) -> int:
        """Return total stored thumbnail contexts."""
        return len(self._store)
