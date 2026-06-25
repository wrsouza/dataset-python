"""FastAPI application entry point for the Data Import Pipeline."""

from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from data_import.application.pipelines.csv_importer import CSVImporter
from data_import.application.pipelines.json_importer import JSONImporter
from data_import.application.pipelines.xml_importer import XMLImporter
from data_import.domain.entities import ImportResult, ImportStatus
from data_import.domain.interfaces import DataImporter
from data_import.infrastructure.job_store import JobStore

app = FastAPI(
    title="Data Import Pipeline",
    description=(
        "Template Method pattern: CSV / JSON / XML importers share one algorithm."
    ),
    version="0.1.0",
)


async def _run_import(file: UploadFile, importer: DataImporter) -> JSONResponse:
    """Save upload to temp file, run importer, store result."""
    suffix = Path(file.filename or "upload").suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    result: ImportResult = importer.import_data(tmp_path)
    JobStore.save(result)

    return JSONResponse(
        status_code=200 if result.status == ImportStatus.COMPLETED else 207,
        content={
            "job_id": result.job_id,
            "status": result.status,
            "report": _serialise_report(result),
        },
    )


def _serialise_report(result: ImportResult) -> dict:  # type: ignore[type-arg]
    if result.report is None:
        return {}
    r = result.report
    return {
        "format": r.format,
        "total_records": r.total_records,
        "persisted_count": r.persisted_count,
        "failed_count": r.failed_count,
        "duration_seconds": round(r.duration_seconds, 4),
        "errors": [
            {"row": e.row_index, "field": e.field, "message": e.message}
            for e in r.errors
        ],
    }


@app.post("/import/csv", summary="Import records from a CSV file")
async def import_csv(file: UploadFile) -> JSONResponse:
    return await _run_import(file, CSVImporter())


@app.post("/import/json", summary="Import records from a JSON file")
async def import_json(file: UploadFile) -> JSONResponse:
    return await _run_import(file, JSONImporter())


@app.post("/import/xml", summary="Import records from an XML file")
async def import_xml(file: UploadFile) -> JSONResponse:
    return await _run_import(file, XMLImporter())


@app.get("/import/{job_id}/status", summary="Get import job status")
async def get_job_status(job_id: str) -> JSONResponse:
    result = JobStore.get(job_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
    return JSONResponse(
        content={
            "job_id": result.job_id,
            "status": result.status,
            "error_message": result.error_message,
            "report": _serialise_report(result),
        }
    )
