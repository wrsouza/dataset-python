"""Composition helpers for wiring the moderation chain to AWS Rekognition."""

from __future__ import annotations

import os

from moderation.domain.interfaces import ModerationHandler
from moderation.infrastructure.handlers import build_moderation_chain
from moderation.infrastructure.rekognition_client import (
    ImageModerationClient,
    RekognitionImageModerationClient,
)


def build_chain(image_client: ImageModerationClient | None = None) -> ModerationHandler:
    """Build the default moderation chain, defaulting to a real Rekognition client."""
    client = image_client or RekognitionImageModerationClient(
        region_name=os.environ.get("AWS_REGION", "us-east-1")
    )
    return build_moderation_chain(client)
