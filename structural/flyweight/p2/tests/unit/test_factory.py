"""Tests for ThumbnailSpecFactory — verifies Flyweight sharing."""

from __future__ import annotations

import dataclasses

import pytest

from thumbnails.domain.entities import ThumbnailSpec
from thumbnails.infrastructure.factory import ThumbnailSpecFactory


def test_get_or_create_returns_same_instance_for_identical_params() -> None:
    """Core Flyweight guarantee: same params → same object reference."""
    factory = ThumbnailSpecFactory()
    spec_a = factory.get_or_create(300, 300, 80, "JPEG", ("thumbnail",))
    spec_b = factory.get_or_create(300, 300, 80, "JPEG", ("thumbnail",))

    assert spec_a is spec_b, "Factory must return the same object for identical params"


def test_get_or_create_returns_different_instance_for_different_params() -> None:
    """Different params must produce different Flyweights."""
    factory = ThumbnailSpecFactory()
    spec_a = factory.get_or_create(300, 300, 80, "JPEG", ("thumbnail",))
    spec_b = factory.get_or_create(600, 600, 85, "JPEG", ("thumbnail",))

    assert spec_a is not spec_b


def test_flyweight_is_frozen() -> None:
    """ThumbnailSpec must be immutable — mutation raises FrozenInstanceError."""
    factory = ThumbnailSpecFactory()
    spec = factory.get_or_create(120, 120, 75, "JPEG", ("thumbnail",))

    with pytest.raises(dataclasses.FrozenInstanceError):
        spec.width = 999  # type: ignore[misc]


def test_named_specs_are_preloaded() -> None:
    """Factory must have named specs ready on construction."""
    factory = ThumbnailSpecFactory()
    assert factory.get_named("thumb_sm") is not None
    assert factory.get_named("avatar") is not None
    assert factory.get_named("banner") is not None


def test_named_spec_returns_same_instance_as_get_or_create() -> None:
    """Named spec and explicit get_or_create with same params share the object."""
    factory = ThumbnailSpecFactory()
    named = factory.get_named("thumb_sm")
    assert named is not None

    by_params = factory.get_or_create(
        width=named.width,
        height=named.height,
        quality=named.quality,
        format=named.format,
        filters=named.filters,
    )
    assert named is by_params


def test_spec_count_reflects_unique_flyweights() -> None:
    """spec_count should grow only when new unique params are requested."""
    factory = ThumbnailSpecFactory()
    initial = factory.spec_count()

    # Requesting same params twice must not increase count
    factory.get_or_create(999, 999, 50, "WEBP", ())
    factory.get_or_create(999, 999, 50, "WEBP", ())
    assert factory.spec_count() == initial + 1

    # Requesting new params should increase count by one
    factory.get_or_create(1, 1, 1, "PNG", ("blur",))
    assert factory.spec_count() == initial + 2


def test_unknown_named_spec_returns_none() -> None:
    factory = ThumbnailSpecFactory()
    assert factory.get_named("non_existent_spec") is None


def test_thumbnail_spec_validation_rejects_invalid_quality() -> None:
    with pytest.raises(ValueError, match="Quality"):
        ThumbnailSpec(width=100, height=100, quality=0, format="JPEG", filters=())


def test_thumbnail_spec_validation_rejects_zero_dimensions() -> None:
    with pytest.raises(ValueError, match="positive"):
        ThumbnailSpec(width=0, height=100, quality=80, format="JPEG", filters=())


def test_thumbnail_spec_validation_rejects_unknown_format() -> None:
    with pytest.raises(ValueError, match="format"):
        ThumbnailSpec(width=100, height=100, quality=80, format="BMP", filters=())


def test_spec_key_is_deterministic() -> None:
    """Same params must produce the same spec_key string."""
    spec_a = ThumbnailSpec(300, 300, 80, "JPEG", ("sharpen", "thumbnail"))
    spec_b = ThumbnailSpec(300, 300, 80, "JPEG", ("sharpen", "thumbnail"))
    assert spec_a.spec_key == spec_b.spec_key


def test_get_all_specs_returns_all_named() -> None:
    factory = ThumbnailSpecFactory()
    specs = factory.get_all_specs()
    assert len(specs) >= 6  # at least the 6 predefined ones
    assert "thumb_sm" in specs
    assert "thumb_md" in specs
    assert "webp_sm" in specs
