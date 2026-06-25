"""Initial migration — creates FileUpload table."""

from __future__ import annotations

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies: list[tuple[str, str]] = []

    operations = [
        migrations.CreateModel(
            name="FileUpload",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.CharField(help_text="Object key in the storage provider", max_length=512)),
                (
                    "provider",
                    models.CharField(
                        choices=[
                            ("s3", "Amazon S3 / LocalStack"),
                            ("gcs", "Google Cloud Storage"),
                            ("azure", "Azure Blob Storage"),
                        ],
                        max_length=16,
                    ),
                ),
                ("size", models.PositiveBigIntegerField(help_text="File size in bytes")),
                ("url", models.URLField(help_text="Public URL of the uploaded object", max_length=1024)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-uploaded_at"],
            },
        ),
        migrations.AddIndex(
            model_name="fileupload",
            index=models.Index(fields=["provider"], name="cloud_adapt_provide_idx"),
        ),
    ]
