"""Unit tests for the Content Export Visitor use cases."""

from __future__ import annotations

import pytest

from content_export_visitor.application.use_cases import (
    ExportContentInput,
    ExportContentUseCase,
    GetExportJobUseCase,
)
from content_export_visitor.domain.exceptions import (
    ExportJobNotFoundError,
    InvalidFormatError,
    InvalidNodeTypeError,
)
from content_export_visitor.infrastructure.repository import DjangoExportJobRepository

pytestmark = pytest.mark.django_db


class FakeS3Client:
    def __init__(self) -> None:
        self.put_calls: list[tuple[str, str, bytes]] = []

    def put_object(self, Bucket: str, Key: str, Body: bytes) -> dict[str, object]:
        self.put_calls.append((Bucket, Key, Body))
        return {}


def test_export_content_uploads_to_s3_and_logs_job() -> None:
    s3_client = FakeS3Client()
    use_case = ExportContentUseCase(DjangoExportJobRepository(), s3_client, "my-bucket")

    job = use_case.execute(
        ExportContentInput(
            format_name="json",
            nodes=[{"type": "article", "title": "A", "body": "B"}],
        )
    )

    assert job.format_name == "json"
    assert job.s3_key.endswith(".json")
    assert len(s3_client.put_calls) == 1
    assert s3_client.put_calls[0][0] == "my-bucket"


def test_export_content_raises_for_unknown_format() -> None:
    use_case = ExportContentUseCase(
        DjangoExportJobRepository(), FakeS3Client(), "my-bucket"
    )

    with pytest.raises(InvalidFormatError):
        use_case.execute(ExportContentInput(format_name="pdf", nodes=[]))


def test_export_content_raises_for_unknown_node_type() -> None:
    use_case = ExportContentUseCase(
        DjangoExportJobRepository(), FakeS3Client(), "my-bucket"
    )

    with pytest.raises(InvalidNodeTypeError):
        use_case.execute(
            ExportContentInput(format_name="json", nodes=[{"type": "unknown"}])
        )


def test_get_export_job_use_case_returns_saved_job() -> None:
    s3_client = FakeS3Client()
    export = ExportContentUseCase(DjangoExportJobRepository(), s3_client, "my-bucket")
    job = export.execute(
        ExportContentInput(
            format_name="markdown",
            nodes=[{"type": "image", "url": "http://x"}],
        )
    )

    found = GetExportJobUseCase(DjangoExportJobRepository()).execute(job.job_id)

    assert found.job_id == job.job_id


def test_get_export_job_use_case_raises_for_unknown_id() -> None:
    use_case = GetExportJobUseCase(DjangoExportJobRepository())

    with pytest.raises(ExportJobNotFoundError):
        use_case.execute("unknown")
