"""AWS Rekognition image moderation client."""

from __future__ import annotations

from typing import Protocol

import boto3


class ImageModerationClient(Protocol):
    """Contract for an image moderation backend."""

    def detect_unsafe_labels(self, image_bytes: bytes) -> list[str]: ...


class RekognitionImageModerationClient:
    """Detects unsafe content in images via AWS Rekognition."""

    def __init__(
        self, confidence_threshold: float = 80.0, region_name: str = "us-east-1"
    ) -> None:
        self._client = boto3.client("rekognition", region_name=region_name)
        self._confidence_threshold = confidence_threshold

    def detect_unsafe_labels(self, image_bytes: bytes) -> list[str]:
        """Return moderation label names above the confidence threshold."""
        response = self._client.detect_moderation_labels(Image={"Bytes": image_bytes})
        return [
            label["Name"]
            for label in response.get("ModerationLabels", [])
            if label["Confidence"] >= self._confidence_threshold
        ]
