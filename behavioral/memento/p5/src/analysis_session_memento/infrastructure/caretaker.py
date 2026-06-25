"""MongoDB Caretaker — persists and retrieves AnalysisSnapshots.

Each snapshot is stored as its own document in the `snapshots`
collection, keyed by `(session_id, version)`. A MongoDB collection
gives natural document storage for the free-form `parameters`/`results`
dicts, which is exactly what the Caretaker needs without imposing a
fixed schema on the analysis itself.

OCP: this is the concrete implementation. Swap with a different backend
by creating another class implementing AnalysisCaretaker ABC.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, cast

from pymongo.collection import Collection

from analysis_session_memento.domain.entities import AnalysisSnapshot, NoHistoryError
from analysis_session_memento.domain.interfaces import AnalysisCaretaker


class MongoAnalysisCaretaker(AnalysisCaretaker):
    """Stores analysis snapshots (mementos) in a MongoDB collection.

    SRP: only manages snapshot persistence — does not interpret the
    contents of `parameters`/`results`.
    """

    def __init__(self, collection: Collection[dict[str, Any]]) -> None:
        self._collection = collection

    def save(self, session_id: str, snapshot: AnalysisSnapshot) -> None:
        self._collection.update_one(
            {"session_id": session_id, "version": snapshot.version},
            {
                "$set": {
                    "parameters": snapshot.parameters,
                    "results": snapshot.results,
                    "label": snapshot.label,
                    "created_at": snapshot.created_at,
                }
            },
            upsert=True,
        )

    def undo(self, session_id: str) -> AnalysisSnapshot:
        docs = list(
            self._collection.find({"session_id": session_id})
            .sort("version", -1)
            .limit(2)
        )
        if len(docs) < 2:
            raise NoHistoryError(session_id)
        self._collection.delete_one(
            {"session_id": session_id, "version": docs[0]["version"]}
        )
        return self._doc_to_snapshot(docs[1])

    def latest(self, session_id: str) -> AnalysisSnapshot:
        doc = self._collection.find_one(
            {"session_id": session_id}, sort=[("version", -1)]
        )
        if doc is None:
            raise NoHistoryError(session_id)
        return self._doc_to_snapshot(doc)

    def history(self, session_id: str) -> list[AnalysisSnapshot]:
        docs = self._collection.find({"session_id": session_id}).sort("version", 1)
        return [self._doc_to_snapshot(doc) for doc in docs]

    @staticmethod
    def _doc_to_snapshot(doc: dict[str, Any]) -> AnalysisSnapshot:
        created_at = cast(datetime, doc["created_at"])
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=UTC)
        return AnalysisSnapshot(
            parameters=dict(doc["parameters"]),
            results=dict(doc["results"]),
            version=int(doc["version"]),
            label=str(doc["label"]),
            created_at=created_at,
        )
