"""Composition helpers — builds the concrete MongoDB collection from env vars."""

from __future__ import annotations

import os
from typing import Any

from pymongo import MongoClient
from pymongo.collection import Collection


def build_snapshots_collection() -> Collection[dict[str, Any]]:
    uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.environ.get("MONGO_DB_NAME", "analysis_sessions")
    client: MongoClient[dict[str, Any]] = MongoClient(uri)
    return client[db_name]["snapshots"]
