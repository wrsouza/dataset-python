"""Tests for application use cases — layout calculation and cache statistics."""

from __future__ import annotations

from fontrender.application.use_cases import (
    GetCacheStatisticsUseCase,
    RenderTextUseCase,
)
from fontrender.domain.entities import FontStyle
from fontrender.infrastructure.glyph_factory import GlyphFactoryImpl


class TestRenderTextUseCase:
    def test_renders_one_positioned_glyph_per_character(self) -> None:
        factory = GlyphFactoryImpl()
        use_case = RenderTextUseCase(factory=factory)
        style = FontStyle(font_family="Arial", size=12, weight="regular")

        result = use_case.execute("AB", style)

        assert len(result) == 2
        assert result[0].glyph.char == "A"
        assert result[1].glyph.char == "B"

    def test_x_positions_accumulate_by_glyph_width(self) -> None:
        factory = GlyphFactoryImpl()
        use_case = RenderTextUseCase(factory=factory)
        style = FontStyle(font_family="Arial", size=12, weight="regular")

        result = use_case.execute("AB", style)

        assert result[0].x == 0
        assert result[1].x == result[0].glyph.width
        assert result[0].y == 0
        assert result[1].y == 0

    def test_newline_resets_x_and_advances_y(self) -> None:
        factory = GlyphFactoryImpl()
        use_case = RenderTextUseCase(factory=factory)
        style = FontStyle(font_family="Arial", size=12, weight="regular")

        result = use_case.execute("A\nB", style)

        assert len(result) == 2
        first, second = result
        assert first.y == 0
        assert second.y > first.y
        assert second.x == 0

    def test_repeated_characters_share_the_same_glyph_instance(self) -> None:
        """Demonstrates Flyweight sharing through the layout use case itself."""
        factory = GlyphFactoryImpl()
        use_case = RenderTextUseCase(factory=factory)
        style = FontStyle(font_family="Arial", size=12, weight="regular")

        result = use_case.execute("AAA", style)

        assert result[0].glyph is result[1].glyph
        assert result[1].glyph is result[2].glyph
        assert factory.unique_glyph_count() == 1


class TestGetCacheStatisticsUseCase:
    def test_statistics_reflect_flyweight_economy(self) -> None:
        factory = GlyphFactoryImpl()
        render_use_case = RenderTextUseCase(factory=factory)
        style = FontStyle(font_family="Arial", size=12, weight="regular")

        text = "AAAA"
        render_use_case.execute(text, style)

        stats_use_case = GetCacheStatisticsUseCase(factory=factory)
        stats = stats_use_case.execute(total_characters=len(text))

        assert stats.total_characters == 4
        assert stats.unique_glyphs == 1
        assert stats.cache_misses == 1
        assert stats.cache_hits == 3
        assert stats.sharing_ratio == 4.0

    def test_savings_percentage_is_zero_when_no_characters_processed(self) -> None:
        factory = GlyphFactoryImpl()
        stats_use_case = GetCacheStatisticsUseCase(factory=factory)

        stats = stats_use_case.execute(total_characters=0)

        assert stats.savings_percentage == 0.0
        assert stats.sharing_ratio == 0.0
