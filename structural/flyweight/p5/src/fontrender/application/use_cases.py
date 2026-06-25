"""Application use cases for the Glyph Font Renderer.

SRP: RenderTextUseCase only computes layout; GetCacheStatisticsUseCase only
reports Flyweight pool economy. Both depend on the GlyphFactory abstraction
(DIP) — never on a concrete factory implementation.
"""

from __future__ import annotations

from dataclasses import dataclass

from fontrender.domain.entities import CacheStatistics, FontStyle, PositionedGlyph
from fontrender.domain.interfaces import GlyphFactory

DEFAULT_LINE_HEIGHT_PADDING = 4
SPACE_CHARACTER = " "


@dataclass
class RenderTextUseCase:
    """Compute the (x, y) layout of a text string using shared Glyph flyweights.

    Extrinsic state (x, y) is calculated here, sequentially, based on each
    Glyph's intrinsic width/height — it is never stored on the Glyph itself.
    """

    factory: GlyphFactory

    def execute(self, text: str, style: FontStyle) -> list[PositionedGlyph]:
        """Lay out `text` left-to-right, wrapping to a new line on '\\n'.

        Args:
            text: The source string to render, one Glyph per character.
            style: Font family, size and weight applied to every character.

        Returns:
            A list of PositionedGlyph (Context objects) — each referencing
            a shared Glyph Flyweight plus its own x/y position.
        """
        positioned: list[PositionedGlyph] = []
        cursor_x = 0
        cursor_y = 0
        line_height = style.size + DEFAULT_LINE_HEIGHT_PADDING

        for char in text:
            if char == "\n":
                cursor_x = 0
                cursor_y += line_height
                continue

            glyph = self.factory.get_or_create(
                char=char,
                font_family=style.font_family,
                size=style.size,
                weight=style.weight,
            )
            positioned.append(PositionedGlyph(glyph=glyph, x=cursor_x, y=cursor_y))
            cursor_x += glyph.width

        return positioned


@dataclass
class GetCacheStatisticsUseCase:
    """Report Flyweight pool economy: unique Glyphs vs total characters processed."""

    factory: GlyphFactory

    def execute(self, total_characters: int) -> CacheStatistics:
        """Build statistics comparing total characters to unique Glyph objects.

        Args:
            total_characters: Number of characters processed in the source
                text (including repeats and whitespace).

        Returns:
            CacheStatistics describing cache hits/misses and the resulting
            sharing ratio / memory savings percentage.
        """
        return CacheStatistics(
            total_characters=total_characters,
            unique_glyphs=self.factory.unique_glyph_count(),
            cache_hits=self.factory.cache_hits(),
            cache_misses=self.factory.cache_misses(),
        )
