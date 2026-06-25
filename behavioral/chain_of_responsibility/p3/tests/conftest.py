"""Shared pytest fixtures for the Content Moderation Pipeline tests."""

from __future__ import annotations

import pytest


class FakeImageModerationClient:
    """A configurable fake ImageModerationClient for unit tests."""

    def __init__(self, labels: list[str] | None = None) -> None:
        self.labels = labels or []

    def detect_unsafe_labels(self, image_bytes: bytes) -> list[str]:
        return self.labels


@pytest.fixture
def fake_image_client() -> FakeImageModerationClient:
    return FakeImageModerationClient()
