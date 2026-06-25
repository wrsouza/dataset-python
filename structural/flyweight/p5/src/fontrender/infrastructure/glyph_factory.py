"""GlyphFactoryImpl — concrete FlyweightFactory caching shared Glyph instances.

Implements the GlyphFactory Protocol (domain/interfaces.py). Depends on a
FontMetricsProvider abstraction rather than a fixed metrics implementation,
so swapping the measurement strategy never requires modifying this factory
(DIP/OCP).
"""

from __future__ import annotations

from fontrender.domain.entities import Glyph
from fontrender.domain.interfaces import FontMetricsProvider
from fontrender.infrastructure.font_metrics import FontMetricsSimulator


class GlyphFactoryImpl:
    """FlyweightFactory — returns the same Glyph instance for identical keys.

    Uses an in-memory dict keyed by (char, font_family, size, weight). The
    same object is returned for identical intrinsic state, which is the
    central guarantee of the Flyweight pattern.
    """

    def __init__(self, metrics_provider: FontMetricsProvider | None = None) -> None:
        self._metrics_provider: FontMetricsProvider = (
            metrics_provider or FontMetricsSimulator()
        )
        self._cache: dict[tuple[str, str, int, str], Glyph] = {}
        self._hits = 0
        self._misses = 0

    def get_or_create(
        self, char: str, font_family: str, size: int, weight: str
    ) -> Glyph:
        """Return the shared Glyph for this key, creating it on first use."""
        cache_key = (char, font_family, size, weight)
        cached = self._cache.get(cache_key)
        if cached is not None:
            self._hits += 1
            return cached

        self._misses += 1
        bitmap, width, height = self._metrics_provider.measure(
            char, font_family, size, weight
        )
        glyph = Glyph(
            char=char,
            font_family=font_family,
            size=size,
            weight=weight,
            bitmap=bitmap,
            width=width,
            height=height,
        )
        self._cache[cache_key] = glyph
        return glyph

    def unique_glyph_count(self) -> int:
        """Return how many distinct Glyph flyweights currently exist."""
        return len(self._cache)

    def cache_hits(self) -> int:
        """Return how many requests were served from the existing cache."""
        return self._hits

    def cache_misses(self) -> int:
        """Return how many requests required creating a new Glyph."""
        return self._misses

    def all_glyphs(self) -> dict[str, Glyph]:
        """Return all cached Glyph flyweights keyed by glyph_key."""
        return {glyph.glyph_key: glyph for glyph in self._cache.values()}

    def reset(self) -> None:
        """Clear the cache and hit/miss counters."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
