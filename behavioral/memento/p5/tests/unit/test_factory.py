"""Unit tests for the MongoDB collection factory."""

from __future__ import annotations

from analysis_session_memento.infrastructure.factory import build_snapshots_collection


def test_build_snapshots_collection_uses_env_defaults() -> None:
    collection = build_snapshots_collection()

    assert collection.name == "snapshots"
    assert collection.database.name == "analysis_sessions"
