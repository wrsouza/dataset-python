"""CLI entry point — Typer-based S3-to-MySQL data processing pipelines.

Composition root: the only place where the concrete S3 client is
built. Each command wires up one ConcreteClass of DataProcessingPipeline.

Usage:
    python -m data_processing_pipeline.main process-csv my-bucket data.csv
    python -m data_processing_pipeline.main process-json my-bucket data.jsonl
"""

from __future__ import annotations

import typer

from data_processing_pipeline.application.pipelines.csv_pipeline import (
    CSVDataProcessingPipeline,
)
from data_processing_pipeline.application.pipelines.json_pipeline import (
    JSONDataProcessingPipeline,
)
from data_processing_pipeline.domain.entities import ProcessingResult
from data_processing_pipeline.infrastructure.s3_factory import build_s3_client

app = typer.Typer(
    name="data-processing-pipeline",
    help="Template Method pattern demo: process S3 objects into MySQL.",
    add_completion=False,
)


def _print_result(result: ProcessingResult) -> None:
    typer.echo(
        f"[{result.pipeline_name}] processed {result.records_processed}, "
        f"persisted {result.records_persisted}"
    )


@app.command(name="process-csv")
def process_csv(bucket: str, key: str) -> None:
    """Process a CSV object from S3 and persist the cleaned rows."""
    pipeline = CSVDataProcessingPipeline(build_s3_client(), bucket, key)
    _print_result(pipeline.process())


@app.command(name="process-json")
def process_json(bucket: str, key: str) -> None:
    """Process a JSON Lines object from S3 and persist the cleaned rows."""
    pipeline = JSONDataProcessingPipeline(build_s3_client(), bucket, key)
    _print_result(pipeline.process())


if __name__ == "__main__":
    app()
