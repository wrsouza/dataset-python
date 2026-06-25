"""Tests for thumbnail use cases with in-memory fakes."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from thumbnails.application.use_cases import (
    GenerateThumbnailUseCase,
    GetFactoryStatsUseCase,
    GetThumbnailUseCase,
)
from thumbnails.domain.exceptions import ImageNotFoundError, UnknownSpecError
from thumbnails.infrastructure.factory import ThumbnailSpecFactory
from thumbnails.infrastructure.repository import InMemoryThumbnailRepository


def _make_fake_storage(has_image: bool = True) -> MagicMock:
    storage = MagicMock()
    if has_image:
        # Minimal 1x1 JPEG bytes for testing
        import io

        from PIL import Image

        buf = io.BytesIO()
        img = Image.new("RGB", (400, 400), color=(100, 150, 200))
        img.save(buf, format="JPEG")
        storage.download.return_value = buf.getvalue()
    else:
        storage.download.side_effect = ImageNotFoundError("missing.jpg")
    storage.upload.return_value = "thumb_key"
    storage.exists.return_value = has_image
    storage.get_url.return_value = "http://localhost/thumb"
    return storage


class TestGenerateThumbnailUseCase:
    def test_generates_and_stores_thumbnail(self) -> None:
        factory = ThumbnailSpecFactory()
        repo = InMemoryThumbnailRepository()
        storage = _make_fake_storage()

        use_case = GenerateThumbnailUseCase(
            storage=storage, repository=repo, factory=factory
        )
        thumb = use_case.execute("photo.jpg", "thumb_sm")

        assert thumb.image_key == "photo.jpg"
        assert thumb.spec.width == 120
        assert repo.count() == 1

    def test_returns_cached_thumbnail_on_second_call(self) -> None:
        factory = ThumbnailSpecFactory()
        repo = InMemoryThumbnailRepository()
        storage = _make_fake_storage()

        use_case = GenerateThumbnailUseCase(
            storage=storage, repository=repo, factory=factory
        )
        first = use_case.execute("photo.jpg", "thumb_sm")
        second = use_case.execute("photo.jpg", "thumb_sm")

        # Storage should only be called once
        storage.download.assert_called_once()
        assert first is second

    def test_raises_unknown_spec_error(self) -> None:
        factory = ThumbnailSpecFactory()
        repo = InMemoryThumbnailRepository()
        storage = _make_fake_storage()

        use_case = GenerateThumbnailUseCase(
            storage=storage, repository=repo, factory=factory
        )
        with pytest.raises(UnknownSpecError):
            use_case.execute("photo.jpg", "nonexistent_spec")

    def test_raises_image_not_found_error(self) -> None:
        factory = ThumbnailSpecFactory()
        repo = InMemoryThumbnailRepository()
        storage = _make_fake_storage(has_image=False)

        use_case = GenerateThumbnailUseCase(
            storage=storage, repository=repo, factory=factory
        )
        with pytest.raises(ImageNotFoundError):
            use_case.execute("missing.jpg", "thumb_sm")


class TestGetFactoryStatsUseCase:
    def test_stats_reflect_flyweight_economy(self) -> None:
        factory = ThumbnailSpecFactory()
        repo = InMemoryThumbnailRepository()
        storage = _make_fake_storage()

        gen_uc = GenerateThumbnailUseCase(
            storage=storage, repository=repo, factory=factory
        )
        gen_uc.execute("a.jpg", "thumb_sm")
        gen_uc.execute("b.jpg", "thumb_sm")  # same spec → reuse Flyweight
        gen_uc.execute("c.jpg", "avatar")

        stats_uc = GetFactoryStatsUseCase(factory=factory, repository=repo)
        stats = stats_uc.execute()

        # unique_specs reflects the whole factory pool (named specs are
        # preloaded at construction), not just the specs actually referenced
        # by a thumbnail — so it stays constant regardless of usage.
        assert stats.total_thumbnails == 3
        assert stats.unique_specs == factory.spec_count()
        assert stats.sharing_ratio == pytest.approx(
            stats.total_thumbnails / stats.unique_specs
        )


class TestGetThumbnailUseCase:
    def test_returns_existing_thumbnail(self) -> None:
        factory = ThumbnailSpecFactory()
        repo = InMemoryThumbnailRepository()
        storage = _make_fake_storage()

        gen_uc = GenerateThumbnailUseCase(
            storage=storage, repository=repo, factory=factory
        )
        gen_uc.execute("img.png", "avatar")

        get_uc = GetThumbnailUseCase(repository=repo, factory=factory)
        thumb = get_uc.execute("img.png", "avatar")
        assert thumb.image_key == "img.png"

    def test_raises_not_found_for_missing_thumbnail(self) -> None:
        factory = ThumbnailSpecFactory()
        repo = InMemoryThumbnailRepository()

        get_uc = GetThumbnailUseCase(repository=repo, factory=factory)
        with pytest.raises(ImageNotFoundError):
            get_uc.execute("never_generated.jpg", "thumb_sm")
