"""MongoDB infrastructure for document and template persistence."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from bson import ObjectId
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from documents.domain.entities import (
    DocumentNotFoundError,
    DocumentRecord,
    TemplateNotFoundError,
    TemplateRecord,
)


class MongoTemplateRepository:
    """Repository for document templates stored in MongoDB.

    SRP: only manages template CRUD — no business logic.
    """

    def __init__(self, collection: Collection) -> None:  # type: ignore[type-arg]
        self._collection = collection

    def save(self, doc_type: str, title: str, content: str, metadata: dict[str, str]) -> TemplateRecord:
        """Persist a new template and return with generated id."""
        doc: dict[str, Any] = {
            "doc_type": doc_type,
            "title": title,
            "content": content,
            "metadata": metadata,
            "created_at": datetime.utcnow(),
        }
        result = self._collection.insert_one(doc)
        return TemplateRecord(
            id=str(result.inserted_id),
            doc_type=doc_type,
            title=title,
            content=content,
            metadata=metadata,
            created_at=doc["created_at"],
        )

    def find_all(self) -> list[TemplateRecord]:
        """Return all stored templates."""
        records = []
        for doc in self._collection.find():
            records.append(self._to_record(doc))
        return records

    def find_by_id(self, template_id: str) -> TemplateRecord:
        """Find template by MongoDB ObjectId string."""
        try:
            oid = ObjectId(template_id)
        except Exception as exc:
            raise TemplateNotFoundError(template_id) from exc
        doc = self._collection.find_one({"_id": oid})
        if doc is None:
            raise TemplateNotFoundError(template_id)
        return self._to_record(doc)

    def _to_record(self, doc: dict[str, Any]) -> TemplateRecord:
        return TemplateRecord(
            id=str(doc["_id"]),
            doc_type=doc["doc_type"],
            title=doc["title"],
            content=doc["content"],
            metadata=doc.get("metadata", {}),
            created_at=doc.get("created_at", datetime.utcnow()),
        )


class MongoDocumentRepository:
    """Repository for cloned documents stored in MongoDB."""

    def __init__(self, collection: Collection) -> None:  # type: ignore[type-arg]
        self._collection = collection

    def save(
        self,
        template_id: str,
        doc_type: str,
        title: str,
        content: str,
        metadata: dict[str, str],
        substitutions: dict[str, str],
    ) -> DocumentRecord:
        """Persist a cloned document."""
        doc: dict[str, Any] = {
            "template_id": template_id,
            "doc_type": doc_type,
            "title": title,
            "content": content,
            "metadata": metadata,
            "substitutions": substitutions,
            "created_at": datetime.utcnow(),
        }
        result = self._collection.insert_one(doc)
        return DocumentRecord(
            id=str(result.inserted_id),
            template_id=template_id,
            doc_type=doc_type,
            title=title,
            content=content,
            metadata=metadata,
            substitutions=substitutions,
            created_at=doc["created_at"],
        )

    def find_by_id(self, document_id: str) -> DocumentRecord:
        """Find a document by its id."""
        try:
            oid = ObjectId(document_id)
        except Exception as exc:
            raise DocumentNotFoundError(document_id) from exc
        doc = self._collection.find_one({"_id": oid})
        if doc is None:
            raise DocumentNotFoundError(document_id)
        return DocumentRecord(
            id=str(doc["_id"]),
            template_id=doc["template_id"],
            doc_type=doc["doc_type"],
            title=doc["title"],
            content=doc["content"],
            metadata=doc.get("metadata", {}),
            substitutions=doc.get("substitutions", {}),
            created_at=doc.get("created_at", datetime.utcnow()),
        )


def create_mongo_client(mongo_uri: str) -> MongoClient:  # type: ignore[type-arg]
    """Create a MongoDB client from the connection URI."""
    return MongoClient(mongo_uri)


def get_repositories(
    client: MongoClient,  # type: ignore[type-arg]
    db_name: str,
) -> tuple[MongoTemplateRepository, MongoDocumentRepository]:
    """Create and return both repositories bound to the given database."""
    db: Database = client[db_name]  # type: ignore[type-arg]
    return (
        MongoTemplateRepository(db["templates"]),
        MongoDocumentRepository(db["documents"]),
    )
