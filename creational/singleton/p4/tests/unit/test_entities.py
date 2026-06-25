"""Unit tests for domain entities."""

from __future__ import annotations

from src.logger.domain.entities import LoggerStats, LogLevel, LogRecord


def test_log_level_label_matches_name() -> None:
    assert LogLevel.ERROR.label == "ERROR"


def test_log_record_to_dict_merges_contexts() -> None:
    record = LogRecord(
        timestamp="2026-01-01T00:00:00+00:00",
        level=LogLevel.INFO,
        message="hello",
        module="mymod",
        context={"a": 1},
        logger_ctx={"b": 2},
    )

    assert record.to_dict() == {
        "timestamp": "2026-01-01T00:00:00+00:00",
        "level": "INFO",
        "message": "hello",
        "module": "mymod",
        "context": {"b": 2, "a": 1},
    }


def test_logger_stats_increment_tracks_counts_by_level() -> None:
    stats = LoggerStats()

    stats.increment(LogLevel.INFO)
    stats.increment(LogLevel.INFO)
    stats.increment(LogLevel.ERROR)

    assert stats.records_emitted == 3
    assert stats.records_by_level == {"INFO": 2, "ERROR": 1}
