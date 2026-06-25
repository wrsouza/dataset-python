"""Domain-specific exceptions for the thumbnail service."""

from __future__ import annotations


class ThumbnailError(Exception):
    """Base exception for thumbnail domain errors."""


class ImageNotFoundError(ThumbnailError):
    def __init__(self, image_key: str) -> None:
        self.image_key = image_key
        super().__init__(f"Image not found in storage: {image_key!r}")


class ThumbnailGenerationError(ThumbnailError):
    def __init__(self, image_key: str, reason: str) -> None:
        self.image_key = image_key
        self.reason = reason
        super().__init__(f"Failed to generate thumbnail for {image_key!r}: {reason}")


class UnknownSpecError(ThumbnailError):
    def __init__(self, spec_name: str) -> None:
        self.spec_name = spec_name
        super().__init__(f"Unknown thumbnail spec: {spec_name!r}")
