"""Unit tests for the Singleton metaclass and StructuredLogger."""

from __future__ import annotations

import threading

from src.logger.domain.entities import LogLevel
from src.logger.handlers.stdout_handler import StdoutJsonHandler
from src.logger.infrastructure.singleton import SingletonMeta, StructuredLogger


def test_returns_same_instance_on_repeated_construction() -> None:
    first = StructuredLogger()
    second = StructuredLogger()

    assert first is second


def test_constructor_args_only_apply_on_first_creation() -> None:
    first = StructuredLogger(min_level=LogLevel.DEBUG)
    second = StructuredLogger(min_level=LogLevel.CRITICAL)

    assert first is second
    assert second._min_level == LogLevel.DEBUG


def test_thread_safety_creates_exactly_one_instance() -> None:
    instances: list[StructuredLogger] = []
    barrier = threading.Barrier(20)

    def _create() -> None:
        barrier.wait()
        instances.append(StructuredLogger())

    threads = [threading.Thread(target=_create) for _ in range(20)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len(instances) == 20
    assert len({id(instance) for instance in instances}) == 1


def test_distinct_singleton_classes_have_independent_instances() -> None:
    class OtherSingleton(metaclass=SingletonMeta):
        pass

    logger = StructuredLogger()
    other = OtherSingleton()

    assert logger is not other
    assert isinstance(logger, StructuredLogger)
    assert isinstance(other, OtherSingleton)


def test_log_emits_record_with_merged_context() -> None:
    logger = StructuredLogger()
    logger.set_context(service="billing")

    record = logger.log(LogLevel.INFO, "payment processed", order_id="o-1")

    assert record.context == {"order_id": "o-1"}
    assert record.logger_ctx == {"service": "billing"}
    assert record.to_dict()["context"] == {"service": "billing", "order_id": "o-1"}


def test_log_below_min_level_is_not_dispatched_to_handlers() -> None:
    logger = StructuredLogger(min_level=LogLevel.WARNING)
    emitted: list[str] = []

    class _SpyHandler:
        def emit(self, record: object) -> None:
            emitted.append("called")

    logger.add_handler(_SpyHandler())
    logger.log(LogLevel.DEBUG, "should not be dispatched")

    assert emitted == []
    assert logger.stats.records_emitted == 0


def test_log_at_or_above_min_level_updates_stats() -> None:
    logger = StructuredLogger(min_level=LogLevel.INFO)
    logger.log(LogLevel.INFO, "first")
    logger.log(LogLevel.ERROR, "second")

    assert logger.stats.records_emitted == 2
    assert logger.stats.records_by_level == {"INFO": 1, "ERROR": 1}


def test_clear_context_removes_global_context() -> None:
    logger = StructuredLogger()
    logger.set_context(request_id="abc")
    logger.clear_context()

    record = logger.log(LogLevel.INFO, "after clear")

    assert record.logger_ctx == {}
    assert logger.stats.active_context_keys == []


def test_add_handler_increments_handler_count() -> None:
    logger = StructuredLogger()
    logger.add_handler(StdoutJsonHandler())

    assert logger.stats.handler_count == 1


def test_convenience_methods_use_expected_levels() -> None:
    logger = StructuredLogger(min_level=LogLevel.DEBUG)

    assert logger.debug("d").level == LogLevel.DEBUG
    assert logger.info("i").level == LogLevel.INFO
    assert logger.warning("w").level == LogLevel.WARNING
    assert logger.error("e").level == LogLevel.ERROR
    assert logger.critical("c").level == LogLevel.CRITICAL
