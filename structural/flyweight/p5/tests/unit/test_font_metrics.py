"""Tests for FontMetricsSimulator — deterministic, extensible metrics catalog."""

from __future__ import annotations

from fontrender.infrastructure.font_metrics import FontMetricsSimulator


def test_measure_is_deterministic_for_the_same_key() -> None:
    simulator = FontMetricsSimulator()

    first = simulator.measure("A", "Arial", 12, "regular")
    second = simulator.measure("A", "Arial", 12, "regular")

    assert first == second


def test_measure_differs_for_bold_weight() -> None:
    simulator = FontMetricsSimulator()

    regular_bitmap, regular_width, _ = simulator.measure("A", "Arial", 12, "regular")
    bold_bitmap, bold_width, _ = simulator.measure("A", "Arial", 12, "bold")

    assert bold_width >= regular_width
    assert regular_bitmap != bold_bitmap


def test_measure_uses_default_profile_for_unknown_font_family() -> None:
    simulator = FontMetricsSimulator()

    bitmap, width, height = simulator.measure("A", "ComicSans2000", 12, "regular")

    assert width > 0
    assert height > 0
    assert "ComicSans2000" in bitmap
