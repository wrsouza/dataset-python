"""Domain entities for the Glyph Font Renderer — Flyweight pattern.

Glyph is the Flyweight: a frozen dataclass sharing intrinsic state
(character, font family, size, weight, simulated bitmap and metrics)
across every occurrence of the same character/font/size/weight combination
inside a rendered text. PositionedGlyph is the Context: it pairs a shared
Glyph reference with extrinsic state (x, y) that is unique per occurrence.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Glyph:
    """Flyweight — intrinsic state shared by every occurrence of a character.

    frozen=True enforces immutability at runtime, making it safe to share a
    single instance across thousands of character occurrences in a text
    without risking accidental mutation. The character, font family, size
    and weight, together with the derived bitmap and metrics, are identical
    for every occurrence of the same key — storing them once instead of once
    per occurrence is the whole memory-saving point of Flyweight.
    """

    char: str
    font_family: str
    size: int
    weight: str
    bitmap: str
    width: int
    height: int

    def __post_init__(self) -> None:
        if len(self.char) != 1:
            raise ValueError("Glyph.char must be exactly one character.")
        if self.size <= 0:
            raise ValueError("Glyph.size must be a positive integer.")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Glyph width/height must be positive integers.")

    @property
    def glyph_key(self) -> str:
        """Stable string key identifying this Glyph's intrinsic state."""
        return f"{self.char}|{self.font_family}|{self.size}|{self.weight}"

    def __repr__(self) -> str:
        return (
            f"Glyph({self.char!r}, font={self.font_family}, "
            f"size={self.size}, weight={self.weight}, "
            f"{self.width}x{self.height})"
        )


@dataclass(frozen=True)
class PositionedGlyph:
    """Context — extrinsic state (x, y) combined with a shared Glyph reference.

    The same Glyph object (the Flyweight) is referenced by every
    PositionedGlyph created for that character/font/size/weight combination
    within a rendered text. Only the position varies per occurrence.
    """

    glyph: Glyph
    x: int
    y: int

    def __repr__(self) -> str:
        return f"PositionedGlyph(char={self.glyph.char!r}, x={self.x}, y={self.y})"


@dataclass(frozen=True)
class FontStyle:
    """Value object describing the requested font configuration.

    Bundles font_family/size/weight so application services accept a single
    parameter instead of three loose primitives (clean code: avoid
    parameter lists that grow with every new attribute).
    """

    font_family: str
    size: int
    weight: str = "regular"

    def __post_init__(self) -> None:
        if self.size <= 0:
            raise ValueError("FontStyle.size must be a positive integer.")


@dataclass(frozen=True)
class CacheStatistics:
    """Statistics showing the Flyweight pool economy for a rendered text.

    total_characters counts every character processed in the source text
    (including repeats); unique_glyphs counts the distinct Glyph Flyweights
    actually created by the factory. The gap between the two numbers is the
    memory saved by sharing.
    """

    total_characters: int
    unique_glyphs: int
    cache_hits: int
    cache_misses: int

    @property
    def sharing_ratio(self) -> float:
        """Average number of character occurrences sharing each Glyph."""
        if self.unique_glyphs == 0:
            return 0.0
        return self.total_characters / self.unique_glyphs

    @property
    def savings_percentage(self) -> float:
        """Percentage of Glyph object creations avoided thanks to caching."""
        if self.total_characters == 0:
            return 0.0
        return (self.cache_hits / self.total_characters) * 100
