"""Simulated font metrics — deterministic FontMetricsProvider implementation.

OCP: new font families are registered by adding an entry to FONT_METRIC_PROFILES
below — no existing code (factory, use cases) needs to change. There is no
if/elif chain keyed on font_family; the catalog is a plain extensible mapping.
"""

from __future__ import annotations

from dataclasses import dataclass

BASE_CHAR_WIDTH_RATIO = 0.6
WEIGHT_WIDTH_MULTIPLIER: dict[str, float] = {
    "regular": 1.0,
    "bold": 1.15,
    "light": 0.92,
}
DEFAULT_WIDTH_MULTIPLIER = 1.0


@dataclass(frozen=True)
class FontMetricProfile:
    """Extensible per-family metric profile — new entries require no code change."""

    width_ratio: float
    height_ratio: float


# Catalog of supported font families — extend this dict to support a new
# family without touching FontMetricsSimulator or any other module (OCP).
FONT_METRIC_PROFILES: dict[str, FontMetricProfile] = {
    "Arial": FontMetricProfile(width_ratio=0.60, height_ratio=1.20),
    "Times New Roman": FontMetricProfile(width_ratio=0.55, height_ratio=1.15),
    "Courier New": FontMetricProfile(width_ratio=0.65, height_ratio=1.25),
    "Verdana": FontMetricProfile(width_ratio=0.64, height_ratio=1.22),
    "Georgia": FontMetricProfile(width_ratio=0.58, height_ratio=1.18),
}
DEFAULT_PROFILE = FontMetricProfile(
    width_ratio=BASE_CHAR_WIDTH_RATIO, height_ratio=1.20
)


def _simulate_bitmap(char: str, font_family: str, size: int, weight: str) -> str:
    """Build a deterministic textual 'bitmap' stand-in for the given key."""
    code_point = ord(char)
    pattern_seed = (code_point * size) % 256
    return f"<bitmap:{font_family}:{weight}:{size}:{char!r}:{pattern_seed:02x}>"


class FontMetricsSimulator:
    """Deterministic FontMetricsProvider — no real font files are rendered.

    Width/height are derived purely from the (char, font_family, size,
    weight) key so the same key always produces identical metrics, which
    keeps Glyph creation reproducible and testable.
    """

    def measure(
        self, char: str, font_family: str, size: int, weight: str
    ) -> tuple[str, int, int]:
        """Return (bitmap, width, height) computed from the profile catalog."""
        profile = FONT_METRIC_PROFILES.get(font_family, DEFAULT_PROFILE)
        weight_multiplier = WEIGHT_WIDTH_MULTIPLIER.get(
            weight, DEFAULT_WIDTH_MULTIPLIER
        )

        width = max(1, round(size * profile.width_ratio * weight_multiplier))
        height = max(1, round(size * profile.height_ratio))
        bitmap = _simulate_bitmap(char, font_family, size, weight)
        return bitmap, width, height
