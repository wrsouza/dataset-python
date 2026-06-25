"""Unit tests for LoadStats aggregate properties."""

from __future__ import annotations

from lazy_loading.domain.entities import LoadStats


def test_total_loads_sums_all_categories() -> None:
    stats = LoadStats(
        profile_loads=1, avatar_loads=2, documents_loads=3, analytics_loads=4
    )

    assert stats.total_loads == 10


def test_total_cache_hits_sums_all_categories() -> None:
    stats = LoadStats(
        profile_cache_hits=1,
        avatar_cache_hits=2,
        documents_cache_hits=3,
        analytics_cache_hits=4,
    )

    assert stats.total_cache_hits == 10
