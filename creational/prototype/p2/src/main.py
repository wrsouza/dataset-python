"""Flask application entry point for the Document Template Cloner."""
from __future__ import annotations

import os
from typing import Any

from flask import Flask, jsonify, request
from pymongo import MongoClient

from documents.application.use_cases import (
    CloneDocumentUseCase,
    CreateTemplateUseCase,
    GetDocumentUseCase,
    ListTemplatesUseCase,
)
from documents.domain.entities import DocumentNotFoundError, TemplateNotFoundError
from documents.infrastructure.mongodb import get_repositories

MONGO_URI = os.getenv("MONGO_URI", "mongodb://app:secret@mongodb:27017/")
MONGO_DB = os.getenv("MONGO_DB", "documents_db")

app = Flask(__name__)

mongo_client: MongoClient = MongoClient(MONGO_URI)  # type: ignore[type-arg]
template_repo, document_repo = get_repositories(mongo_client, MONGO_DB)


# ── Template routes ─────────────────────────────────────────────────────────


@app.post("/templates")
def create_template() -> tuple[Any, int]:
    """Create a new document template."""
    data: dict[str, Any] = request.get_json() or {}
    doc_type = data.get("doc_type", "")
    title = data.get("title", "")
    content = data.get("content", "")
    metadata = data.get("metadata", {})

    if not doc_type or not title or not content:
        return jsonify({"error": "doc_type, title and content are required"}), 400

    try:
        use_case = CreateTemplateUseCase(template_repo)
        record = use_case.execute(doc_type, title, content, metadata)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return (
        jsonify(
            {
                "id": record.id,
                "doc_type": record.doc_type,
                "title": record.title,
            }
        ),
        201,
    )


@app.get("/templates")
def list_templates() -> Any:
    """List all document templates."""
    use_case = ListTemplatesUseCase(template_repo)
    records = use_case.execute()
    return jsonify(
        [
            {
                "id": r.id,
                "doc_type": r.doc_type,
                "title": r.title,
                "placeholders": [],
            }
            for r in records
        ]
    )


# ── Document (clone) routes ─────────────────────────────────────────────────


@app.post("/documents/clone/<template_id>")
def clone_document(template_id: str) -> tuple[Any, int]:
    """Clone a template with provided substitutions."""
    data: dict[str, Any] = request.get_json() or {}
    substitutions: dict[str, str] = data.get("substitutions", {})

    try:
        use_case = CloneDocumentUseCase(template_repo, document_repo)
        record = use_case.execute(template_id, substitutions)
    except TemplateNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404

    return (
        jsonify(
            {
                "id": record.id,
                "template_id": record.template_id,
                "doc_type": record.doc_type,
                "title": record.title,
                "content": record.content,
            }
        ),
        201,
    )


@app.get("/documents/<document_id>")
def get_document(document_id: str) -> tuple[Any, int]:
    """Retrieve a cloned document by id."""
    try:
        use_case = GetDocumentUseCase(document_repo)
        record = use_case.execute(document_id)
    except DocumentNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404

    return (
        jsonify(
            {
                "id": record.id,
                "template_id": record.template_id,
                "doc_type": record.doc_type,
                "title": record.title,
                "content": record.content,
                "metadata": record.metadata,
                "substitutions": record.substitutions,
            }
        ),
        200,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
