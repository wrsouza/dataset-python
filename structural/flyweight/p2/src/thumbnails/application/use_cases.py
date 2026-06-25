"""Application use cases for the thumbnail service — SRP: one class, one action."""

from __future__ import annotations

import io

from PIL import Image, ImageFilter

from thumbnails.domain.entities import FactoryStats, ImageThumbnail, ThumbnailSpec
from thumbnails.domain.exceptions import (
    ImageNotFoundError,
    ThumbnailGenerationError,
    UnknownSpecError,
)
from thumbnails.domain.interfaces import (
    ImageStorageProtocol,
    ThumbnailRepositoryProtocol,
    ThumbnailSpecFactoryProtocol,
)

_PIL_FILTER_MAP: dict[str, type[ImageFilter.Filter]] = {
    "sharpen": ImageFilter.SHARPEN,
    "blur": ImageFilter.BLUR,
    "smooth": ImageFilter.SMOOTH,
    "detail": ImageFilter.DETAIL,
}


def _apply_filters(image: Image.Image, filters: tuple[str, ...]) -> Image.Image:
    """Apply named PIL filters to the image."""
    for f in filters:
        if f == "thumbnail":
            continue  # handled separately as resize operation
        if f == "antialias":
            continue  # antialias is a resampling option, not a filter
        pil_filter = _PIL_FILTER_MAP.get(f)
        if pil_filter:
            image = image.filter(pil_filter())
    return image


def _process_image(raw: bytes, spec: ThumbnailSpec) -> bytes:
    """Convert raw bytes into a thumbnail according to the shared ThumbnailSpec."""
    try:
        with Image.open(io.BytesIO(raw)) as opened:
            converted: Image.Image = opened.convert(
                "RGBA" if spec.format == "PNG" else "RGB"
            )
            converted.thumbnail((spec.width, spec.height), Image.Resampling.LANCZOS)
            converted = _apply_filters(converted, spec.filters)

            output = io.BytesIO()
            save_kwargs: dict[str, object] = {"quality": spec.quality}
            if spec.format == "PNG":
                # PNG does not support quality — use compression level
                save_kwargs = {"compress_level": max(0, min(9, 9 - spec.quality // 11))}
            converted.save(output, format=spec.format, **save_kwargs)
            return output.getvalue()
    except Exception as exc:
        raise ThumbnailGenerationError("unknown", str(exc)) from exc


class GenerateThumbnailUseCase:
    """Generate a thumbnail for the given image using the shared ThumbnailSpec.

    SRP: this class only generates and stores thumbnails.
    DIP: depends on protocols, not concrete implementations.
    """

    def __init__(
        self,
        storage: ImageStorageProtocol,
        repository: ThumbnailRepositoryProtocol,
        factory: ThumbnailSpecFactoryProtocol,
    ) -> None:
        self._storage = storage
        self._repository = repository
        self._factory = factory

    def execute(self, image_key: str, spec_name: str) -> ImageThumbnail:
        """Generate thumbnail or return cached one if it already exists."""
        spec = self._factory.get_named(spec_name)  # type: ignore[attr-defined]
        if spec is None:
            raise UnknownSpecError(spec_name)

        existing = self._repository.find(image_key, spec.spec_key)
        if existing is not None:
            return existing

        raw = self._storage.download(image_key)
        try:
            thumb_bytes = _process_image(raw, spec)
        except ThumbnailGenerationError as exc:
            raise ThumbnailGenerationError(image_key, exc.reason) from exc

        content_type = f"image/{spec.format.lower()}"
        thumbnail_key = f"{image_key}/{spec.spec_key}.{spec.format.lower()}"
        self._storage.upload(thumbnail_key, thumb_bytes, content_type)

        thumbnail = ImageThumbnail(
            image_key=image_key,
            thumbnail_key=thumbnail_key,
            spec=spec,
        )
        self._repository.save(thumbnail)
        return thumbnail


class GetThumbnailUseCase:
    """Retrieve an existing thumbnail context."""

    def __init__(
        self,
        repository: ThumbnailRepositoryProtocol,
        factory: ThumbnailSpecFactoryProtocol,
    ) -> None:
        self._repository = repository
        self._factory = factory

    def execute(self, image_key: str, spec_name: str) -> ImageThumbnail:
        spec = self._factory.get_named(spec_name)  # type: ignore[attr-defined]
        if spec is None:
            raise UnknownSpecError(spec_name)
        result = self._repository.find(image_key, spec.spec_key)
        if result is None:
            raise ImageNotFoundError(f"{image_key}/{spec_name}")
        return result


class GetFactoryStatsUseCase:
    """Return statistics about the Flyweight pool vs total thumbnail contexts."""

    def __init__(
        self,
        factory: ThumbnailSpecFactoryProtocol,
        repository: ThumbnailRepositoryProtocol,
    ) -> None:
        self._factory = factory
        self._repository = repository

    def execute(self) -> FactoryStats:
        all_specs = self._factory.get_all_specs()
        return FactoryStats(
            unique_specs=self._factory.spec_count(),
            total_thumbnails=self._repository.count(),
            spec_names=sorted(all_specs.keys()),
        )
