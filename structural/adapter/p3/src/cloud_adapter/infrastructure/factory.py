"""Factory — composition root for cloud storage adapters.

Single place in the codebase that knows about concrete SDK clients.
Everything else depends on the CloudStorage Protocol (DIP).
"""

from __future__ import annotations

import os

from cloud_adapter.domain.interfaces import CloudStorage
from cloud_adapter.infrastructure.adapters import (
    AzureStorageAdapter,
    GCSStorageAdapter,
    S3StorageAdapter,
)
from cloud_adapter.infrastructure.fake_clients import FakeAzureClient, FakeGCSClient

# Supported provider identifiers
PROVIDER_S3 = "s3"
PROVIDER_GCS = "gcs"
PROVIDER_AZURE = "azure"
SUPPORTED_PROVIDERS = (PROVIDER_S3, PROVIDER_GCS, PROVIDER_AZURE)


def make_storage(provider: str) -> CloudStorage:
    """Return the CloudStorage adapter for *provider*.

    The caller only ever sees the CloudStorage interface; no SDK leaks out.
    """
    if provider == PROVIDER_S3:
        return _make_s3_adapter()
    if provider == PROVIDER_GCS:
        return _make_gcs_adapter()
    if provider == PROVIDER_AZURE:
        return _make_azure_adapter()
    raise ValueError(f"Unknown provider '{provider}'. Choose from: {SUPPORTED_PROVIDERS}")


# ── Private factories ─────────────────────────────────────────────────────────


def _make_s3_adapter() -> S3StorageAdapter:
    """Build S3 adapter pointing at LocalStack (or real AWS via env vars)."""
    import boto3  # lazy import — only needed when S3 provider is selected

    endpoint_url = os.getenv("AWS_ENDPOINT_URL", "http://localstack:4566")
    bucket = os.getenv("S3_BUCKET", "cloud-adapter-bucket")
    region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

    client = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        region_name=region,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
    )

    # Ensure bucket exists (LocalStack starts empty)
    try:
        client.head_bucket(Bucket=bucket)
    except Exception:
        client.create_bucket(Bucket=bucket)

    return S3StorageAdapter(client, bucket, endpoint_url)


def _make_gcs_adapter() -> GCSStorageAdapter:
    """Build GCS adapter (fake client — no real GCP credentials needed)."""
    bucket = os.getenv("GCS_BUCKET", "cloud-adapter-gcs")
    client = FakeGCSClient(project=os.getenv("GCS_PROJECT", "fake-project"))
    return GCSStorageAdapter(client, bucket)


def _make_azure_adapter() -> AzureStorageAdapter:
    """Build Azure adapter (fake client — no real Azure credentials needed)."""
    container = os.getenv("AZURE_CONTAINER", "cloud-adapter-azure")
    account = os.getenv("AZURE_ACCOUNT_NAME", "fakeaccount")
    key = os.getenv("AZURE_ACCOUNT_KEY", "fakekey")
    client = FakeAzureClient(account_name=account, account_key=key)
    return AzureStorageAdapter(client, container)
