"""Integration test: long repetitive text must reuse Glyph flyweights heavily."""

from __future__ import annotations

from fontrender.application.use_cases import (
    GetCacheStatisticsUseCase,
    RenderTextUseCase,
)
from fontrender.domain.entities import FontStyle
from fontrender.infrastructure.glyph_factory import GlyphFactoryImpl


def test_long_repetitive_text_creates_far_fewer_glyphs_than_characters() -> None:
    """A long, highly repetitive text should create a tiny number of unique Glyphs."""
    factory = GlyphFactoryImpl()
    render_use_case = RenderTextUseCase(factory=factory)
    stats_use_case = GetCacheStatisticsUseCase(factory=factory)
    style = FontStyle(font_family="Arial", size=16, weight="regular")

    sentence = "the quick brown fox jumps over the lazy dog "
    long_text = sentence * 200  # 200 repetitions → thousands of characters

    positioned_glyphs = render_use_case.execute(long_text, style)
    total_characters = len(long_text.replace("\n", ""))
    stats = stats_use_case.execute(total_characters=total_characters)

    distinct_chars_in_alphabet = len(set(sentence))

    assert len(positioned_glyphs) == total_characters
    assert stats.unique_glyphs == distinct_chars_in_alphabet
    assert stats.unique_glyphs < total_characters / 100
    assert stats.sharing_ratio > 100


def test_multiple_font_styles_each_get_their_own_glyph_pool_entries() -> None:
    """Same characters in two different styles must NOT share Glyph instances."""
    factory = GlyphFactoryImpl()
    render_use_case = RenderTextUseCase(factory=factory)

    text = "hello world"
    style_a = FontStyle(font_family="Arial", size=12, weight="regular")
    style_b = FontStyle(font_family="Arial", size=12, weight="bold")

    glyphs_a = render_use_case.execute(text, style_a)
    glyphs_b = render_use_case.execute(text, style_b)

    chars_in_text = len(set(text))
    assert factory.unique_glyph_count() == chars_in_text * 2

    glyphs_a_set = {id(p.glyph) for p in glyphs_a}
    glyphs_b_set = {id(p.glyph) for p in glyphs_b}
    assert glyphs_a_set.isdisjoint(glyphs_b_set)


def test_reset_allows_recomputing_a_fresh_pool() -> None:
    factory = GlyphFactoryImpl()
    render_use_case = RenderTextUseCase(factory=factory)
    style = FontStyle(font_family="Georgia", size=20, weight="light")

    render_use_case.execute("aaaa bbbb", style)
    assert factory.unique_glyph_count() > 0

    factory.reset()
    assert factory.unique_glyph_count() == 0
    assert factory.cache_hits() == 0
    assert factory.cache_misses() == 0

    render_use_case.execute("a", style)
    assert factory.unique_glyph_count() == 1
