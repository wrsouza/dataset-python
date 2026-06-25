"""Directors — orchestrate builders to produce standard compose stacks."""

from __future__ import annotations

from compose_builder.domain.entities import ComposeFile
from compose_builder.domain.interfaces import DockerComposeBuilder

# ---------------------------------------------------------------------------
# Director: FastAPI + PostgreSQL
# ---------------------------------------------------------------------------


class FastAPIWithPostgresDirector:
    """Builds a FastAPI application stack with a PostgreSQL database.

    Stack: fastapi_app + postgres + (optional redis cache).

    DIP: depends on DockerComposeBuilder abstraction, not any concrete builder.
    """

    def __init__(self, builder: DockerComposeBuilder) -> None:
        self._builder = builder

    def build(
        self,
        *,
        app_image: str = "myapp:latest",
        app_port: str = "8000",
        postgres_version: str = "16",
        include_redis: bool = False,
    ) -> ComposeFile:
        """Assemble the FastAPI + Postgres compose file."""
        self._builder.set_version("3.9")

        # PostgreSQL service
        self._builder.add_service(
            name="db",
            image=f"postgres:{postgres_version}-alpine",
            ports=["5432:5432"],
            env={
                "POSTGRES_USER": "${POSTGRES_USER:-app}",
                "POSTGRES_PASSWORD": "${POSTGRES_PASSWORD:-secret}",
                "POSTGRES_DB": "${POSTGRES_DB:-appdb}",
            },
            volumes=["postgres_data:/var/lib/postgresql/data"],
            healthcheck={
                "test": ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-app}"],
                "interval": "5s",
                "timeout": "5s",
                "retries": 5,
            },
        )
        self._builder.add_volume("postgres_data")

        # Optional Redis cache
        depends: list[str] = ["db"]
        if include_redis:
            self._builder.add_service(
                name="cache",
                image="redis:7-alpine",
                ports=["6379:6379"],
                healthcheck={
                    "test": ["CMD", "redis-cli", "ping"],
                    "interval": "5s",
                    "timeout": "3s",
                    "retries": 3,
                },
            )
            depends.append("cache")

        # FastAPI application service
        self._builder.add_service(
            name="app",
            image=app_image,
            ports=[f"{app_port}:8000"],
            env={
                "DATABASE_URL": "postgresql://app:secret@db:5432/appdb",
                "REDIS_URL": "redis://cache:6379" if include_redis else "",
            },
            depends_on=depends,
        )

        return self._builder.build()


# ---------------------------------------------------------------------------
# Director: Django + Redis
# ---------------------------------------------------------------------------


class DjangoWithRedisDirector:
    """Builds a Django application stack with Redis for cache/Celery broker.

    Stack: django_app + redis + postgres.
    """

    def __init__(self, builder: DockerComposeBuilder) -> None:
        self._builder = builder

    def build(
        self,
        *,
        app_image: str = "django-app:latest",
        app_port: str = "8000",
        include_celery: bool = False,
    ) -> ComposeFile:
        """Assemble the Django + Redis + Postgres compose file."""
        self._builder.set_version("3.9")

        # PostgreSQL
        self._builder.add_service(
            name="db",
            image="postgres:16-alpine",
            env={
                "POSTGRES_USER": "${POSTGRES_USER:-django}",
                "POSTGRES_PASSWORD": "${POSTGRES_PASSWORD:-django}",
                "POSTGRES_DB": "${POSTGRES_DB:-django_db}",
            },
            volumes=["pg_data:/var/lib/postgresql/data"],
            healthcheck={
                "test": ["CMD-SHELL", "pg_isready -U django"],
                "interval": "5s",
                "timeout": "5s",
                "retries": 5,
            },
        )
        self._builder.add_volume("pg_data")

        # Redis
        self._builder.add_service(
            name="redis",
            image="redis:7-alpine",
            ports=["6379:6379"],
        )

        # Django app
        self._builder.add_service(
            name="web",
            image=app_image,
            ports=[f"{app_port}:8000"],
            env={
                "DJANGO_SETTINGS_MODULE": "config.settings",
                "DATABASE_URL": "postgresql://django:django@db:5432/django_db",
                "CELERY_BROKER_URL": "redis://redis:6379/0",
            },
            depends_on=["db", "redis"],
            command="python manage.py runserver 0.0.0.0:8000",
        )

        # Optional Celery worker
        if include_celery:
            self._builder.add_service(
                name="worker",
                image=app_image,
                env={
                    "DATABASE_URL": "postgresql://django:django@db:5432/django_db",
                    "CELERY_BROKER_URL": "redis://redis:6379/0",
                },
                depends_on=["db", "redis"],
                command="celery -A config worker --loglevel=info",
            )

        return self._builder.build()


# ---------------------------------------------------------------------------
# Director: Web + PostgreSQL + Redis
# ---------------------------------------------------------------------------


class WebPostgresRedisDirector:
    """Builds a generic web application stack with PostgreSQL and Redis.

    Stack: web app + postgres + redis. This is the canonical "web-postgres-redis"
    preset offered by the CLI.
    """

    def __init__(self, builder: DockerComposeBuilder) -> None:
        self._builder = builder

    def build(
        self,
        *,
        app_image: str = "web-app:latest",
        app_port: str = "8000",
    ) -> ComposeFile:
        """Assemble the web + postgres + redis compose file."""
        self._builder.set_version("3.9")

        self._builder.add_service(
            name="db",
            image="postgres:16-alpine",
            ports=["5432:5432"],
            env={
                "POSTGRES_USER": "${POSTGRES_USER:-app}",
                "POSTGRES_PASSWORD": "${POSTGRES_PASSWORD:-secret}",
                "POSTGRES_DB": "${POSTGRES_DB:-appdb}",
            },
            volumes=["db_data:/var/lib/postgresql/data"],
            healthcheck={
                "test": ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-app}"],
                "interval": "5s",
                "timeout": "5s",
                "retries": 5,
            },
        )
        self._builder.add_volume("db_data")

        self._builder.add_service(
            name="cache",
            image="redis:7-alpine",
            ports=["6379:6379"],
            healthcheck={
                "test": ["CMD", "redis-cli", "ping"],
                "interval": "5s",
                "timeout": "3s",
                "retries": 3,
            },
        )

        self._builder.add_service(
            name="web",
            image=app_image,
            ports=[f"{app_port}:8000"],
            env={
                "DATABASE_URL": "postgresql://app:secret@db:5432/appdb",
                "REDIS_URL": "redis://cache:6379",
            },
            depends_on=["db", "cache"],
        )

        return self._builder.build()


# ---------------------------------------------------------------------------
# Director: Kafka Stack
# ---------------------------------------------------------------------------


class KafkaStackDirector:
    """Builds a Kafka event-streaming stack.

    Stack: zookeeper + kafka + (optional) kafka-ui + postgres sink.
    """

    def __init__(self, builder: DockerComposeBuilder) -> None:
        self._builder = builder

    def build(
        self,
        *,
        kafka_version: str = "7.6.0",
        include_ui: bool = True,
        include_postgres_sink: bool = False,
    ) -> ComposeFile:
        """Assemble the Kafka stack compose file."""
        self._builder.set_version("3.9")
        self._builder.add_network("kafka_net", driver="bridge")

        # Zookeeper
        self._builder.add_service(
            name="zookeeper",
            image=f"confluentinc/cp-zookeeper:{kafka_version}",
            env={
                "ZOOKEEPER_CLIENT_PORT": "2181",
                "ZOOKEEPER_TICK_TIME": "2000",
            },
            ports=["2181:2181"],
            networks=["kafka_net"],
        )

        # Kafka broker
        self._builder.add_service(
            name="kafka",
            image=f"confluentinc/cp-kafka:{kafka_version}",
            depends_on=["zookeeper"],
            ports=["9092:9092"],
            env={
                "KAFKA_BROKER_ID": "1",
                "KAFKA_ZOOKEEPER_CONNECT": "zookeeper:2181",
                "KAFKA_ADVERTISED_LISTENERS": (
                    "PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092"
                ),
                "KAFKA_LISTENER_SECURITY_PROTOCOL_MAP": (
                    "PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT"
                ),
                "KAFKA_INTER_BROKER_LISTENER_NAME": "PLAINTEXT",
                "KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR": "1",
            },
            volumes=["kafka_data:/var/lib/kafka/data"],
            networks=["kafka_net"],
            healthcheck={
                "test": [
                    "CMD",
                    "kafka-broker-api-versions",
                    "--bootstrap-server",
                    "localhost:9092",
                ],
                "interval": "10s",
                "timeout": "10s",
                "retries": 5,
            },
        )
        self._builder.add_volume("kafka_data")

        # Optional Kafka UI
        if include_ui:
            self._builder.add_service(
                name="kafka-ui",
                image="provectuslabs/kafka-ui:latest",
                ports=["8080:8080"],
                depends_on=["kafka"],
                env={
                    "KAFKA_CLUSTERS_0_NAME": "local",
                    "KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS": "kafka:29092",
                },
                networks=["kafka_net"],
            )

        # Optional PostgreSQL sink
        if include_postgres_sink:
            self._builder.add_service(
                name="postgres",
                image="postgres:16-alpine",
                ports=["5432:5432"],
                env={
                    "POSTGRES_USER": "kafka",
                    "POSTGRES_PASSWORD": "kafka",
                    "POSTGRES_DB": "events",
                },
                volumes=["pg_sink_data:/var/lib/postgresql/data"],
                networks=["kafka_net"],
            )
            self._builder.add_volume("pg_sink_data")

        return self._builder.build()
