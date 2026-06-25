"""Application use cases for the Content Export Visitor system.

`ExportContentUseCase` picks the right ConcreteVisitor for the
requested format, traverses the content nodes, uploads the rendered
output to S3, and logs the job.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from content_export_visitor.application.node_factory import build_nodes
from content_export_visitor.application.structure import traverse
from content_export_visitor.domain.entities import ExportJob
from content_export_visitor.infrastructure.repository import DjangoExportJobRepository
from content_export_visitor.infrastructure.s3_factory import S3ClientLike
from content_export_visitor.infrastructure.visitors.registry import get_visitor


@dataclass
class ExportContentInput:
    format_name: str
    nodes: list[dict[str, Any]]


class ExportContentUseCase:
    def __init__(
        self,
        repository: DjangoExportJobRepository,
        s3_client: S3ClientLike,
        bucket: str,
    ) -> None:
        self._repository = repository
        self._s3_client = s3_client
        self._bucket = bucket

    def execute(self, data: ExportContentInput) -> ExportJob:
        visitor = get_visitor(data.format_name)
        nodes = build_nodes(data.nodes)
        result = traverse(nodes, visitor)

        job_id = str(uuid.uuid4())
        s3_key = f"exports/{job_id}{visitor.get_file_extension()}"
        self._s3_client.put_object(
            Bucket=self._bucket, Key=s3_key, Body=result.content.encode("utf-8")
        )

        job = ExportJob(job_id=job_id, format_name=data.format_name, s3_key=s3_key)
        self._repository.save(job)
        return job


class GetExportJobUseCase:
    def __init__(self, repository: DjangoExportJobRepository) -> None:
        self._repository = repository

    def execute(self, job_id: str) -> ExportJob:
        return self._repository.find_by_id(job_id)
