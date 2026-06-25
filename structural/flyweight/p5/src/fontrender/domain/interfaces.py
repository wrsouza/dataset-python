"""Domain interfaces (Protocols) — DIP boundary for the font renderer.

Application services depend only on these Protocols, never on concrete
infrastructure classes. This lets the layout service work with any
GlyphFactory implementation (in-memory cache, Redis-backed cache, etc.)
and any FontMetricsProvider (different metric strategies) without changes.
"""

from __future__ import annotations

from typing import Protocol

from fontrender.domain.entities import CacheStatistics, Glyph


class FontMetricsProvider(Protocol):
    """Strategy that derives simulated bitmap/metrics for a glyph key.

    OCP: new font families or measurement strategies can be added by
    providing a new FontMetricsProvider implementation — the GlyphFactory
    and layout service never need to change.
    """

    def measure(
        self, char: str, font_family: str, size: int, weight: str
    ) -> tuple[str, int, int]:
        """Return (bitmap, width, height) deterministically for the given key."""
        ...


class GlyphFactory(Protocol):
    """FlyweightFactory — manages the pool of shared Glyph flyweights.

    get_or_create must return the SAME Glyph instance for identical
    (char, font_family, size, weight) keys, and a different instance for
    any different key. This is the core Flyweight contract.
    """

    def get_or_create(
        self, char: str, font_family: str, size: int, weight: str
    ) -> Glyph:
        """Return the shared Glyph for this key, creating it on first use."""
        ...

    def unique_glyph_count(self) -> int:
        """Return how many distinct Glyph flyweights currently exist."""
        ...

    def cache_hits(self) -> int:
        """Return how many requests were served from the existing cache."""
        ...

    def cache_misses(self) -> int:
        """Return how many requests required creating a new Glyph."""
        ...

    def all_glyphs(self) -> dict[str, Glyph]:
        """Return all cached Glyph flyweights keyed by glyph_key."""
        ...

    def reset(self) -> None:
        """Clear the cache and hit/miss counters."""
        ...


class TextLayoutService(Protocol):
    """Abstraction for laying out a text string into positioned glyphs."""

    def render(
        self, text: str, font_family: str, size: int, weight: str
    ) -> list[object]:
        """Return a list of PositionedGlyph objects for the given text."""
        ...

    def statistics_for(self, total_characters: int) -> CacheStatistics:
        """Build cache statistics for the most recent render() call."""
        ...
