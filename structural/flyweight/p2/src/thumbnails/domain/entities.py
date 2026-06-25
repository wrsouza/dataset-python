"""Domain entities for Image Thumbnail Cache — Flyweight pattern.

ThumbnailSpec is the Flyweight: frozen dataclass sharing intrinsic state
(dimensions, quality, format, filters) across many ImageThumbnail contexts.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ThumbnailSpec:
    """Flyweight — intrinsic state shared by all thumbnails of the same specification.

    frozen=True enforces immutability at runtime, making this safe to share
    across thousands of ImageThumbnail instances without risk of mutation.
    Width, height, quality, format and filters are identical for all images
    processed under the same spec — storing them once saves significant memory.
    """

    width: int
    height: int
    quality: int
    format: str
    filters: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Width and height must be positive integers.")
        if not (1 <= self.quality <= 100):
            raise ValueError("Quality must be between 1 and 100.")
        if self.format.upper() not in ("JPEG", "PNG", "WEBP", "GIF"):
            raise ValueError(f"Unsupported format: {self.format}")

    @property
    def spec_key(self) -> str:
        """Derive a stable string key from this spec for naming and caching."""
        filters_part = "-".join(sorted(self.filters)) if self.filters else "none"
        return (
            f"{self.width}x{self.height}_{self.quality}q_{self.format}_{filters_part}"
        )

    def __repr__(self) -> str:
        return (
            f"ThumbnailSpec({self.width}x{self.height}, "
            f"q={self.quality}, fmt={self.format}, filters={self.filters})"
        )


@dataclass
class ImageThumbnail:
    """Context — combines extrinsic state (image_key) with a Flyweight reference.

    image_key uniquely identifies the source image — it varies per instance.
    thumbnail_key is the generated S3 key for this specific thumbnail.
    spec is the shared Flyweight containing processing parameters.
    """

    image_key: str
    thumbnail_key: str
    spec: ThumbnailSpec  # shared Flyweight — same object for all images with same spec

    @property
    def s3_path(self) -> str:
        """Build the full S3 path for this thumbnail."""
        return f"thumbnails/{self.thumbnail_key}"

    def __repr__(self) -> str:
        return (
            f"ImageThumbnail(image={self.image_key!r}, "
            f"thumb={self.thumbnail_key!r}, spec={self.spec!r})"
        )


@dataclass(frozen=True)
class FactoryStats:
    """Statistics showing Flyweight pool economy."""

    unique_specs: int
    total_thumbnails: int
    spec_names: list[str]

    @property
    def sharing_ratio(self) -> float:
        """Average number of thumbnails sharing each spec."""
        if self.unique_specs == 0:
            return 0.0
        return self.total_thumbnails / self.unique_specs
