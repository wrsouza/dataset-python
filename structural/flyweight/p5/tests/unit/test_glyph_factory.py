"""Tests for GlyphFactoryImpl — verifies the core Flyweight sharing guarantee."""

from __future__ import annotations

import dataclasses

import pytest

from fontrender.domain.entities import Glyph
from fontrender.infrastructure.glyph_factory import GlyphFactoryImpl


def test_get_or_create_returns_same_instance_for_identical_key() -> None:
    """Core Flyweight guarantee: same key → same object reference."""
    factory = GlyphFactoryImpl()

    glyph_a = factory.get_or_create("A", "Arial", 12, "bold")
    glyph_b = factory.get_or_create("A", "Arial", 12, "bold")

    assert glyph_a is glyph_b, "Factory must return the same object for identical keys"


def test_get_or_create_returns_different_instance_for_different_char() -> None:
    """Different characters must produce different Flyweights."""
    factory = GlyphFactoryImpl()

    glyph_a = factory.get_or_create("A", "Arial", 12, "bold")
    glyph_b = factory.get_or_create("B", "Arial", 12, "bold")

    assert glyph_a is not glyph_b


def test_get_or_create_returns_different_instance_for_different_font() -> None:
    """Same character but different font family must produce different Flyweights."""
    factory = GlyphFactoryImpl()

    glyph_a = factory.get_or_create("A", "Arial", 12, "regular")
    glyph_b = factory.get_or_create("A", "Georgia", 12, "regular")

    assert glyph_a is not glyph_b


def test_get_or_create_returns_different_instance_for_different_size_or_weight() -> (
    None
):
    """Same char/font but different size or weight must produce different Flyweights."""
    factory = GlyphFactoryImpl()

    base = factory.get_or_create("A", "Arial", 12, "regular")
    different_size = factory.get_or_create("A", "Arial", 24, "regular")
    different_weight = factory.get_or_create("A", "Arial", 12, "bold")

    assert base is not different_size
    assert base is not different_weight


def test_glyph_is_frozen() -> None:
    """Glyph must be immutable — mutation raises FrozenInstanceError."""
    factory = GlyphFactoryImpl()
    glyph = factory.get_or_create("A", "Arial", 12, "regular")

    with pytest.raises(dataclasses.FrozenInstanceError):
        glyph.size = 999  # type: ignore[misc]


def test_unique_glyph_count_grows_only_for_new_keys() -> None:
    """unique_glyph_count must grow only when a genuinely new key is requested."""
    factory = GlyphFactoryImpl()

    factory.get_or_create("A", "Arial", 12, "regular")
    factory.get_or_create("A", "Arial", 12, "regular")
    assert factory.unique_glyph_count() == 1

    factory.get_or_create("B", "Arial", 12, "regular")
    assert factory.unique_glyph_count() == 2


def test_cache_hits_and_misses_are_tracked() -> None:
    """First request per key is a miss; subsequent identical requests are hits."""
    factory = GlyphFactoryImpl()

    factory.get_or_create("A", "Arial", 12, "regular")  # miss
    factory.get_or_create("A", "Arial", 12, "regular")  # hit
    factory.get_or_create("A", "Arial", 12, "regular")  # hit
    factory.get_or_create("B", "Arial", 12, "regular")  # miss

    assert factory.cache_misses() == 2
    assert factory.cache_hits() == 2


def test_all_glyphs_returns_every_cached_flyweight() -> None:
    factory = GlyphFactoryImpl()
    factory.get_or_create("A", "Arial", 12, "regular")
    factory.get_or_create("B", "Arial", 12, "regular")

    glyphs = factory.all_glyphs()
    assert len(glyphs) == 2
    assert all(isinstance(g, Glyph) for g in glyphs.values())


def test_reset_clears_cache_and_counters() -> None:
    factory = GlyphFactoryImpl()
    factory.get_or_create("A", "Arial", 12, "regular")
    factory.get_or_create("A", "Arial", 12, "regular")

    factory.reset()

    assert factory.unique_glyph_count() == 0
    assert factory.cache_hits() == 0
    assert factory.cache_misses() == 0


def test_glyph_validation_rejects_multi_character_string() -> None:
    with pytest.raises(ValueError, match="one character"):
        Glyph(
            char="AB",
            font_family="Arial",
            size=12,
            weight="regular",
            bitmap="x",
            width=10,
            height=10,
        )


def test_glyph_validation_rejects_non_positive_size() -> None:
    with pytest.raises(ValueError, match="size"):
        Glyph(
            char="A",
            font_family="Arial",
            size=0,
            weight="regular",
            bitmap="x",
            width=10,
            height=10,
        )


def test_glyph_validation_rejects_non_positive_dimensions() -> None:
    with pytest.raises(ValueError, match="width/height"):
        Glyph(
            char="A",
            font_family="Arial",
            size=12,
            weight="regular",
            bitmap="x",
            width=0,
            height=10,
        )


def test_glyph_key_is_deterministic() -> None:
    """Same key parameters must produce the same glyph_key string."""
    glyph_a = Glyph(
        char="A",
        font_family="Arial",
        size=12,
        weight="bold",
        bitmap="x",
        width=8,
        height=14,
    )
    glyph_b = Glyph(
        char="A",
        font_family="Arial",
        size=12,
        weight="bold",
        bitmap="x",
        width=8,
        height=14,
    )
    assert glyph_a.glyph_key == glyph_b.glyph_key
