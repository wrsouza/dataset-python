"""FlyweightFactory: ThumbnailSpecFactory managing a pool of ThumbnailSpec objects."""

from __future__ import annotations

from typing import TypedDict

from thumbnails.domain.entities import ThumbnailSpec


class _SpecConfig(TypedDict):
    width: int
    height: int
    quality: int
    format: str
    filters: tuple[str, ...]


# Pre-defined named specs that the API can reference by name
NAMED_SPECS: dict[str, _SpecConfig] = {
    "thumb_sm": {
        "width": 120,
        "height": 120,
        "quality": 75,
        "format": "JPEG",
        "filters": ("thumbnail",),
    },
    "thumb_md": {
        "width": 300,
        "height": 300,
        "quality": 80,
        "format": "JPEG",
        "filters": ("thumbnail", "sharpen"),
    },
    "thumb_lg": {
        "width": 600,
        "height": 600,
        "quality": 85,
        "format": "JPEG",
        "filters": ("thumbnail", "sharpen"),
    },
    "banner": {
        "width": 1200,
        "height": 400,
        "quality": 90,
        "format": "JPEG",
        "filters": ("thumbnail",),
    },
    "avatar": {
        "width": 64,
        "height": 64,
        "quality": 85,
        "format": "PNG",
        "filters": ("thumbnail", "antialias"),
    },
    "webp_sm": {
        "width": 200,
        "height": 200,
        "quality": 80,
        "format": "WEBP",
        "filters": ("thumbnail",),
    },
}


class ThumbnailSpecFactory:
    """FlyweightFactory — returns the same ThumbnailSpec instance for identical params.

    Uses an in-memory dict keyed by (width, height, quality, format, filters).
    The same object is returned for identical intrinsic state, proving sharing.
    """

    def __init__(self) -> None:
        self._cache: dict[tuple[int, int, int, str, tuple[str, ...]], ThumbnailSpec] = (
            {}
        )
        self._named: dict[str, ThumbnailSpec] = {}
        self._load_named_specs()

    def _load_named_specs(self) -> None:
        """Pre-populate cache with all named specs."""
        for name, config in NAMED_SPECS.items():
            spec = self.get_or_create(
                width=config["width"],
                height=config["height"],
                quality=config["quality"],
                format=config["format"],
                filters=config["filters"],
            )
            self._named[name] = spec

    def get_or_create(
        self,
        width: int,
        height: int,
        quality: int,
        format: str,
        filters: tuple[str, ...],
    ) -> ThumbnailSpec:
        """Return the shared Flyweight — create and cache if not yet seen."""
        cache_key = (width, height, quality, format.upper(), filters)
        if cache_key not in self._cache:
            self._cache[cache_key] = ThumbnailSpec(
                width=width,
                height=height,
                quality=quality,
                format=format.upper(),
                filters=filters,
            )
        return self._cache[cache_key]

    def get_named(self, name: str) -> ThumbnailSpec | None:
        """Return a pre-defined named spec, or None if unknown."""
        return self._named.get(name)

    def get_all_specs(self) -> dict[str, ThumbnailSpec]:
        """Return all named specs for listing."""
        return dict(self._named)

    def spec_count(self) -> int:
        """Return the number of unique Flyweights in the pool."""
        return len(self._cache)
