"""Unit tests for RekognitionImageModerationClient using moto."""

from __future__ import annotations

from moto import mock_aws

from moderation.infrastructure.rekognition_client import (
    RekognitionImageModerationClient,
)


@mock_aws
def test_detect_unsafe_labels_filters_by_confidence() -> None:
    client = RekognitionImageModerationClient(confidence_threshold=80.0)

    fake_response = {
        "ModerationLabels": [
            {"Name": "Explicit Nudity", "Confidence": 95.0},
            {"Name": "Violence", "Confidence": 40.0},
        ]
    }
    client._client.detect_moderation_labels = lambda **kwargs: fake_response  # type: ignore[method-assign]

    labels = client.detect_unsafe_labels(b"fake-bytes")

    assert labels == ["Explicit Nudity"]


@mock_aws
def test_detect_unsafe_labels_returns_empty_when_no_labels() -> None:
    client = RekognitionImageModerationClient()
    client._client.detect_moderation_labels = lambda **kwargs: {  # type: ignore[method-assign]
        "ModerationLabels": []
    }

    labels = client.detect_unsafe_labels(b"fake-bytes")

    assert labels == []


def test_client_can_be_constructed_with_real_boto3_session() -> None:
    client = RekognitionImageModerationClient(region_name="us-east-1")

    assert client._client.meta.service_model.service_name == "rekognition"
