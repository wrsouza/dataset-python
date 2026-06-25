"""Shared pytest fixtures for the Analysis Session Snapshots tests."""

from __future__ import annotations

from typing import Any

import mongomock
import pytest
from pymongo.collection import Collection

from analysis_session_memento.infrastructure.caretaker import MongoAnalysisCaretaker


@pytest.fixture
def collection() -> Collection[dict[str, Any]]:
    client: mongomock.MongoClient[dict[str, Any]] = mongomock.MongoClient()
    return client["analysis_sessions"]["snapshots"]


@pytest.fixture
def caretaker(collection: Collection[dict[str, Any]]) -> MongoAnalysisCaretaker:
    return MongoAnalysisCaretaker(collection)
