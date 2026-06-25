"""Django model: FileUpload — records each upload in the database."""

from __future__ import annotations

from django.db import models


class FileUpload(models.Model):
    """Persists metadata for every file uploaded via any cloud provider."""

    PROVIDER_CHOICES = [
        ("s3", "Amazon S3 / LocalStack"),
        ("gcs", "Google Cloud Storage"),
        ("azure", "Azure Blob Storage"),
    ]

    key = models.CharField(max_length=512, help_text="Object key in the storage provider")
    provider = models.CharField(max_length=16, choices=PROVIDER_CHOICES)
    size = models.PositiveBigIntegerField(help_text="File size in bytes")
    url = models.URLField(max_length=1024, help_text="Public URL of the uploaded object")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
        indexes = [models.Index(fields=["provider"])]

    def __str__(self) -> str:
        return f"{self.provider}:{self.key}"
