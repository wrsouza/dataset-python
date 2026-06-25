"""Unit tests for Director presets."""

from __future__ import annotations

from compose_builder.application.directors import (
    DjangoWithRedisDirector,
    FastAPIWithPostgresDirector,
    KafkaStackDirector,
    WebPostgresRedisDirector,
)
from compose_builder.infrastructure.builders import (
    MicroservicesComposeBuilder,
    WebAppComposeBuilder,
)


def test_web_postgres_redis_director_builds_three_services() -> None:
    director = WebPostgresRedisDirector(WebAppComposeBuilder())

    compose = director.build()

    assert set(compose.services) == {"db", "cache", "web"}
    assert compose.services["web"].depends_on == ["db", "cache"]


def test_fastapi_with_postgres_director_without_redis() -> None:
    director = FastAPIWithPostgresDirector(WebAppComposeBuilder())

    compose = director.build(include_redis=False)

    assert set(compose.services) == {"db", "app"}
    assert compose.services["app"].depends_on == ["db"]


def test_fastapi_with_postgres_director_with_redis() -> None:
    director = FastAPIWithPostgresDirector(WebAppComposeBuilder())

    compose = director.build(include_redis=True)

    assert set(compose.services) == {"db", "cache", "app"}
    assert compose.services["app"].depends_on == ["db", "cache"]


def test_django_with_redis_director_with_celery() -> None:
    director = DjangoWithRedisDirector(WebAppComposeBuilder())

    compose = director.build(include_celery=True)

    assert set(compose.services) == {"db", "redis", "web", "worker"}


def test_django_with_redis_director_without_celery() -> None:
    director = DjangoWithRedisDirector(WebAppComposeBuilder())

    compose = director.build(include_celery=False)

    assert "worker" not in compose.services


def test_kafka_stack_director_default_includes_ui_no_sink() -> None:
    director = KafkaStackDirector(MicroservicesComposeBuilder())

    compose = director.build()

    assert "kafka-ui" in compose.services
    assert "postgres" not in compose.services
    assert "kafka_net" in compose.networks


def test_kafka_stack_director_with_postgres_sink() -> None:
    director = KafkaStackDirector(MicroservicesComposeBuilder())

    compose = director.build(include_ui=False, include_postgres_sink=True)

    assert "kafka-ui" not in compose.services
    assert "postgres" in compose.services
    assert "pg_sink_data" in compose.volumes
